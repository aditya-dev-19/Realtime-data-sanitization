import os
import sys
import requests
import asyncio
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

# This script assumes your server is running on localhost at port 8000
API_URL = "http://localhost:8000/api"

def test_api_endpoints():
    """
    Tests the encryption and decryption API endpoints.
    """
    print("--- Starting API Endpoint Test ---")
    
    # 1. Define test data (High Sensitivity)
    plaintext = b"This is a secret test message to check if encryption is working correctly."
    filename = "test_api_document.txt"
    sensitivity_score = 0.95
    
    print(f"Original plaintext: {plaintext.decode()}")
    print(f"Original filename: {filename}")
    print(f"Sensitivity score: {sensitivity_score}")
    print("\n--- Sending file to /api/encrypt-upload/ endpoint... ---")

    try:
        # 2. Upload and encrypt the file via the API
        files = {'file': (filename, plaintext, 'application/octet-stream')}
        data = {'sensitivity_score': sensitivity_score}
        
        response = requests.post(f"{API_URL}/encrypt-upload/", files=files, data=data)
        response.raise_for_status() # Raise an exception for bad status codes
        
        upload_result = response.json()
        print("✅ File uploaded and encrypted successfully!")
        print("Response:", upload_result)
        
        firestore_doc_id = upload_result['data']['firestore_doc_id']
        gcs_object_name = upload_result['data']['gcs_object_name']
        encryption_type = upload_result['data']['encryption_type']
        
        print(f"Firestore Document ID: {firestore_doc_id}")
        print(f"GCS Object Name: {gcs_object_name}")
        print(f"Encryption Type: {encryption_type}")
        
        # 3. Download and decrypt the file via the API
        print("\n--- Downloading file from /api/download-decrypt/ endpoint... ---")
        download_response = requests.get(f"{API_URL}/download-decrypt/?firestore_doc_id={firestore_doc_id}")
        download_response.raise_for_status()
        
        recovered_plaintext = download_response.content
        
        print("✅ File downloaded and decrypted successfully!")
        print(f"Recovered plaintext: {recovered_plaintext.decode()}")
        
        # 4. Verify the integrity
        if recovered_plaintext == plaintext:
            print("\n✅ Test Passed: Recovered plaintext matches original. API endpoints are working correctly.")
        else:
            print("\n❌ Test Failed: Recovered plaintext does NOT match original.")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test Failed: An API request error occurred.")
        print(f"Error details: {e}")
        if 'response' in locals() and response is not None:
            print(f"Server response content: {response.text}")
    except Exception as e:
        print(f"❌ Test Failed: An unexpected error occurred.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    # Ensure your FastAPI server is running in a separate terminal before running this script.
    # Command to run the server:
    # uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    test_api_endpoints()