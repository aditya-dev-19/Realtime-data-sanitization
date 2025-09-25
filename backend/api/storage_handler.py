# backend/api/storage_handler.py
import os
import time
import base64
import hashlib
from typing import Tuple, Optional, Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from google.cloud import storage
from google.cloud import kms
from google.cloud import firestore

# ---------------------------
# Configuration (from env)
# ---------------------------
GCS_BUCKET = os.environ.get("GCS_BUCKET", "my-sanitized-files-bucket")
KMS_PROJECT = os.environ.get("KMS_PROJECT")
KMS_LOCATION = os.environ.get("KMS_LOCATION", "global")
KMS_KEY_RING = os.environ.get("KMS_KEY_RING")
KMS_CRYPTO_KEY = os.environ.get("KMS_CRYPTO_KEY")
FIRESTORE_COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "file_storage_metadata")

# sanity checks
if not all([KMS_PROJECT, KMS_KEY_RING, KMS_CRYPTO_KEY]):
    # don't fail import in dev; functions will raise later if KMS not configured
    pass

# ---------------------------
# Clients (lazy init)
# ---------------------------
_storage_client = None
_kms_client = None
_firestore_client = None

def _get_storage_client():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client

def _get_kms_client():
    global _kms_client
    if _kms_client is None:
        _kms_client = kms.KeyManagementServiceClient()
    return _kms_client

def _get_firestore_client():
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client

def _kms_key_name():
    if not (KMS_PROJECT and KMS_LOCATION and KMS_KEY_RING and KMS_CRYPTO_KEY):
        raise RuntimeError("KMS configuration missing. Set KMS_PROJECT, KMS_LOCATION, KMS_KEY_RING, KMS_CRYPTO_KEY")
    return _get_kms_client().crypto_key_path(KMS_PROJECT, KMS_LOCATION, KMS_KEY_RING, KMS_CRYPTO_KEY)

# ---------------------------
# Crypto helpers
# ---------------------------

def generate_dek(bit_length: int = 256) -> bytes:
    if bit_length not in (128, 256):
        raise ValueError("bit_length must be 128 or 256")
    if bit_length == 128:
        return AESGCM.generate_key(bit_length=128)
    return AESGCM.generate_key(bit_length=256)

def encrypt_with_cipher(plaintext: bytes, dek: bytes, cipher_name: str) -> Tuple[bytes, bytes]:
    """
    Return (nonce, ciphertext)
    cipher_name in {'AESGCM', 'ChaCha20Poly1305'}
    """
    if cipher_name == "AESGCM":
        aesgcm = AESGCM(dek)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce, ciphertext
    elif cipher_name == "ChaCha20Poly1305":
        chacha = ChaCha20Poly1305(dek)
        nonce = os.urandom(12)  # 96-bit nonce is fine for chacha in cryptography
        ciphertext = chacha.encrypt(nonce, plaintext, None)
        return nonce, ciphertext
    else:
        raise ValueError("Unsupported cipher: " + cipher_name)

def decrypt_with_cipher(nonce: bytes, ciphertext: bytes, dek: bytes, cipher_name: str) -> bytes:
    if cipher_name == "AESGCM":
        aesgcm = AESGCM(dek)
        return aesgcm.decrypt(nonce, ciphertext, None)
    elif cipher_name == "ChaCha20Poly1305":
        chacha = ChaCha20Poly1305(dek)
        return chacha.decrypt(nonce, ciphertext, None)
    else:
        raise ValueError("Unsupported cipher: " + cipher_name)

# ---------------------------
# KMS wrapping
# ---------------------------

def wrap_dek_with_kms(dek: bytes) -> bytes:
    client = _get_kms_client()
    name = _kms_key_name()
    # Using KMS encrypt API to wrap the DEK
    resp = client.encrypt(request={"name": name, "plaintext": dek})
    return resp.ciphertext

def unwrap_dek_with_kms(wrapped_dek: bytes) -> bytes:
    client = _get_kms_client()
    name = _kms_key_name()
    resp = client.decrypt(request={"name": name, "ciphertext": wrapped_dek})
    return resp.plaintext

# ---------------------------
# GCS helpers
# ---------------------------

def upload_ciphertext_to_gcs(object_name: str, data: bytes, content_type: str = "application/octet-stream", metadata: Optional[Dict]=None) -> None:
    client = _get_storage_client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(object_name)
    if metadata:
        blob.metadata = metadata
    blob.upload_from_string(data, content_type=content_type)

def download_ciphertext_from_gcs(object_name: str) -> bytes:
    client = _get_storage_client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()

# ---------------------------
# Firestore metadata helpers
# ---------------------------

def save_metadata_to_firestore(doc_id: str, meta: Dict) -> None:
    db = _get_firestore_client()
    coll = db.collection(FIRESTORE_COLLECTION)
    coll.document(doc_id).set(meta)

def load_metadata_from_firestore(doc_id: str) -> Optional[Dict]:
    db = _get_firestore_client()
    doc = db.collection(FIRESTORE_COLLECTION).document(doc_id).get()
    if not doc.exists:
        return None
    return doc.to_dict()

# ---------------------------
# Adaptive cipher selection
# ---------------------------

def choose_cipher_for_sensitivity(sensitivity: float) -> Tuple[str, int]:
    """
    Return (cipher_name, dek_bits)
    sensitivity in [0,1]
    """
    if sensitivity >= 0.85:
        return "AESGCM", 256
    if sensitivity >= 0.5:
        # ChaCha20Poly1305 is high-performance on CPUs without AES hardware
        return "ChaCha20Poly1305", 256
    # lower sensitivity -> AES-128 (still AEAD)
    return "AESGCM", 128

# ---------------------------
# Public API
# ---------------------------

def encrypt_and_upload_file(
    file_bytes: bytes,
    original_filename: str,
    sensitivity: float,
    uploader_id: Optional[str] = None,
    model_version: Optional[str] = None
) -> Dict:
    """
    Encrypt file_bytes according to sensitivity, upload to GCS, store metadata in Firestore.
    Returns metadata dict including object_name and firestore_doc_id.
    """
    if not (0.0 <= sensitivity <= 1.0):
        raise ValueError("sensitivity must be in [0,1]")

    cipher_name, dek_bits = choose_cipher_for_sensitivity(sensitivity)

    # 1) generate DEK
    dek = generate_dek(bit_length=dek_bits)

    # 2) encrypt
    nonce, ciphertext = encrypt_with_cipher(file_bytes, dek, cipher_name)

    # 3) wrap DEK with KMS
    wrapped_dek = wrap_dek_with_kms(dek)

    # 4) compute SHA-256 for integrity
    sha256_hex = hashlib.sha256(file_bytes).hexdigest()

    # 5) object name + firestore doc id
    ts = int(time.time())
    safe_name = os.path.basename(original_filename)
    object_name = f"sanitized/{ts}_{safe_name}"
    firestore_doc_id = f"{ts}_{safe_name}"

    # 6) upload to GCS (store some metadata on the object as well)
    obj_metadata = {"sensitivity": str(sensitivity), "cipher": cipher_name}
    upload_ciphertext_to_gcs(object_name, ciphertext, metadata=obj_metadata)

    # 7) store metadata in Firestore (wrapped_dek and nonce are binary -> store base64)
    meta_doc = {
        "original_filename": original_filename,
        "object_name": object_name,
        "wrapped_dek_b64": base64.b64encode(wrapped_dek).decode("utf-8"),
        "nonce_b64": base64.b64encode(nonce).decode("utf-8"),
        "cipher": cipher_name,
        "sensitivity": float(sensitivity),
        "content_sha256": sha256_hex,
        "uploaded_at": firestore.SERVER_TIMESTAMP,
    }
    if uploader_id:
        meta_doc["uploader_id"] = uploader_id
    if model_version:
        meta_doc["model_version"] = model_version

    save_metadata_to_firestore(firestore_doc_id, meta_doc)

    return {"object_name": object_name, "firestore_doc_id": firestore_doc_id, "cipher": cipher_name}


def download_and_decrypt_file_by_doc(firestore_doc_id: str) -> Tuple[bytes, Dict]:
    """
    Given a Firestore doc id, fetch metadata, download ciphertext from GCS, unwrap DEK with KMS,
    decrypt and return plaintext + metadata.
    """
    meta = load_metadata_from_firestore(firestore_doc_id)
    if not meta:
        raise FileNotFoundError("Metadata not found in Firestore: " + firestore_doc_id)

    object_name = meta["object_name"]
    ciphertext = download_ciphertext_from_gcs(object_name)

    wrapped_dek_b64 = meta["wrapped_dek_b64"]
    nonce_b64 = meta["nonce_b64"]
    cipher_name = meta["cipher"]

    wrapped_dek = base64.b64decode(wrapped_dek_b64)
    nonce = base64.b64decode(nonce_b64)

    # unwrap
    dek = unwrap_dek_with_kms(wrapped_dek)

    # decrypt
    plaintext = decrypt_with_cipher(nonce, ciphertext, dek, cipher_name)

    # verify integrity
    computed = hashlib.sha256(plaintext).hexdigest()
    if computed != meta.get("content_sha256"):
        raise ValueError("SHA-256 mismatch: possible tampering or corruption")

    return plaintext, meta