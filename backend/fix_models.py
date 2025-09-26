#!/usr/bin/env python3
"""
Script to re-download models from Google Cloud Storage and fix corruption issues.
"""

import os
import sys
from pathlib import Path
from google.cloud import storage

def download_models_from_gcs(bucket_name: str, destination_folder: str = "downloaded_models"):
    """
    Downloads all files from a specified GCS bucket to a local folder.
    This will overwrite any existing corrupted files.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"Created local directory for models: {destination_folder}")

        print(f"Starting model download from GCS bucket '{bucket_name}'...")
        downloaded_files = 0

        for blob in blobs:
            destination_file_name = os.path.join(destination_folder, blob.name)
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

            # Download the file
            blob.download_to_filename(destination_file_name)
            downloaded_files += 1
            print(f"✅ Downloaded {blob.name} ({blob.size} bytes)")

        print(f"Successfully downloaded {downloaded_files} files from GCS.")
        return True

    except Exception as e:
        print(f"❌ Error downloading models: {e}")
        return False

def verify_model_files(model_dir: str):
    """Verify that model files are not corrupted."""
    model_dir = Path(model_dir)

    print("🔍 Verifying model files...")

    # Check phishing model
    phishing_path = model_dir / "phishing_model_v2"
    if phishing_path.exists():
        config_file = phishing_path / "config.json"
        model_file = phishing_path / "model.safetensors"

        if config_file.exists() and model_file.exists():
            try:
                import json
                with open(config_file) as f:
                    config = json.load(f)

                # Check file sizes
                model_size = model_file.stat().st_size
                print(f"✅ Phishing model: {model_size} bytes, labels: {config.get('id2label', {})}")

                if model_size < 1000:  # Very small files are likely corrupted
                    print(f"⚠️ Warning: Phishing model file seems small ({model_size} bytes)")
                    return False

            except Exception as e:
                print(f"❌ Phishing model verification failed: {e}")
                return False
        else:
            print("❌ Phishing model files missing")
            return False

    # Check code injection model
    code_injection_path = model_dir / "code_injection_model_prod"
    if code_injection_path.exists():
        config_file = code_injection_path / "config.json"
        model_file = code_injection_path / "model.safetensors"

        if config_file.exists() and model_file.exists():
            try:
                import json
                with open(config_file) as f:
                    config = json.load(f)

                # Check file sizes
                model_size = model_file.stat().st_size
                print(f"✅ Code injection model: {model_size} bytes, labels: {config.get('id2label', {})}")

                if model_size < 1000:  # Very small files are likely corrupted
                    print(f"⚠️ Warning: Code injection model file seems small ({model_size} bytes)")
                    return False

            except Exception as e:
                print(f"❌ Code injection model verification failed: {e}")
                return False
        else:
            print("❌ Code injection model files missing")
            return False

    return True

def main():
    """Main function to re-download and verify models."""
    print("🔄 Re-downloading models from Google Cloud Storage...")
    print("=" * 60)

    # Re-download models
    bucket_name = "realtime-data-sanitization-models"
    success = download_models_from_gcs(bucket_name)

    if not success:
        print("❌ Failed to download models. Please check your GCS permissions and bucket name.")
        return 1

    print("\n" + "=" * 60)
    print("✅ Model download completed!")

    # Verify models
    print("\n" + "=" * 60)
    model_dir = "downloaded_models"
    if verify_model_files(model_dir):
        print("✅ All model files verified successfully!")
        print("\n🚀 You can now restart your FastAPI server and test the comprehensive analysis endpoint.")
        print("   The phishing and code injection models should now work correctly.")
    else:
        print("❌ Model verification failed. Some files may still be corrupted.")
        print("   Try running this script again or check your GCS bucket contents.")

    return 0

if __name__ == "__main__":
    exit(main())
