# test_encryption.py
import os
import sys
import io
from pathlib import Path
from dotenv import dotenv_values

# Manually load environment variables from the .env file
# This bypasses potential issues with load_dotenv()
try:
    project_root = Path(__file__).resolve().parent
    env_path = os.path.join(project_root, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_vars = dotenv_values(stream=f)
            for key, value in env_vars.items():
                if value is not None:
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env file.")
    else:
        print("⚠️ .env file not found. Falling back to system environment variables.")

except Exception as e:
    print(f"❌ Error loading .env file: {e}")
    
# Add project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from api.storage_handler import encrypt_and_upload_file, download_and_decrypt_file_by_doc

def test_encryption_roundtrip():
    """
    Tests the full encryption, upload, download, and decryption flow.
    """
    print("--- Starting Encryption Test ---")
    
    # Check if a necessary environment variable is set
    if not os.environ.get("KMS_PROJECT"):
        print("❌ Error: KMS configuration is missing. Please check your .env file.")
        print("Make sure it contains KMS_PROJECT, KMS_LOCATION, KMS_KEY_RING, and KMS_CRYPTO_KEY.")
        return

    # 1. Define test data
    plaintext = b"This is a secret test message to check if encryption is working correctly."
    original_filename = "test_document.txt"
    sensitivity_score = 0.95  # Use a high sensitivity score for AES-256-GCM

    print(f"Original plaintext: {plaintext.decode()}")
    print(f"Original filename: {original_filename}")
    print(f"Sensitivity score: {sensitivity_score}")
    print("\n--- Encrypting and Uploading... ---")

    try:
        # 2. Encrypt and upload the file
        result = encrypt_and_upload_file(
            file_bytes=plaintext,
            original_filename=original_filename,
            sensitivity=sensitivity_score
        )
        firestore_doc_id = result["firestore_doc_id"]
        object_name = result["object_name"]

        print("✅ Encryption and upload successful!")
        print(f"Firestore Document ID: {firestore_doc_id}")
        print(f"GCS Object Name: {object_name}")

        print("\n--- Downloading and Decrypting... ---")
        
        # 3. Download and decrypt the file
        recovered_plaintext, metadata = download_and_decrypt_file_by_doc(firestore_doc_id)
        
        print("✅ Download and decryption successful!")
        print(f"Recovered plaintext: {recovered_plaintext.decode()}")
        print(f"Retrieved metadata: {metadata}")

        # 4. Verify the integrity
        assert recovered_plaintext == plaintext
        assert metadata["original_filename"] == original_filename
        print("\n✅ Test Passed: Recovered plaintext matches original. Encryption is working correctly.")

    except Exception as e:
        print(f"❌ Test Failed: An error occurred.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_encryption_roundtrip()