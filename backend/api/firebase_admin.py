# Updated firebase_admin.py with proper Cloud Run configuration
# Replace your backend/api/firebase_admin.py with this content

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# --- Initialize Firebase Admin SDK for Cloud Run ---
print("🔧 Initializing Firebase Admin SDK...")

try:
    # Get project ID from environment variable
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'realtime-data-sanitization')
    print(f"📋 Using project ID: {project_id}")
    
    # Check if Firebase app is already initialized
    try:
        app = firebase_admin.get_app()
        print("✅ Firebase app already initialized")
    except ValueError:
        # Initialize Firebase Admin SDK
        print("🚀 Initializing new Firebase app...")
        
        # For Cloud Run, use Application Default Credentials
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            print(f"✅ Firebase initialized with Application Default Credentials for project: {project_id}")
            
        except Exception as adc_error:
            print(f"⚠️  Application Default Credentials failed: {adc_error}")
            
            # Fallback: Try with service account key from environment
            service_account_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
            if service_account_key:
                try:
                    service_account_info = json.loads(service_account_key)
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
                    print(f"✅ Firebase initialized with service account key for project: {project_id}")
                except Exception as key_error:
                    print(f"⚠️  Service account key initialization failed: {key_error}")
                    raise
            else:
                print("❌ No valid authentication method found")
                raise Exception("Firebase authentication failed - check service account configuration")

    # Initialize Firestore client
    print("🔥 Connecting to Firestore...")
    db = firestore.client()
    
    # Test the connection with a simple operation
    try:
        # Test read operation
        test_collection = db.collection('_firebase_test')
        test_doc_ref = test_collection.document('connection_test')
        
        # Try to set and get a test document
        test_doc_ref.set({
            'test': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firebase connection successful'
        })
        
        # Verify we can read it back
        doc_snapshot = test_doc_ref.get()
        if doc_snapshot.exists:
            print("✅ Firestore connection test successful - data written and read successfully")
            # Clean up test document
            test_doc_ref.delete()
        else:
            print("⚠️  Firestore test document was not found after writing")
            
    except Exception as test_error:
        print(f"⚠️  Firestore connection test failed: {test_error}")
        # Don't fail completely, just warn
        
    print("✅ Firestore client initialized successfully")

except Exception as e:
    print(f"❌ CRITICAL: Firebase initialization failed completely: {e}")
    print(f"❌ Error type: {type(e).__name__}")
    print(f"❌ Error details: {str(e)}")
    
    # Only use mock client as absolute last resort
    print("❌ FALLING BACK TO MOCK CLIENT - DATA WILL NOT BE PERSISTED!")
    
    class MockFirestoreClient:
        def collection(self, name):
            print(f"❌ MOCK: Accessing collection '{name}' - DATA WILL NOT BE SAVED!")
            return MockCollection(name)
    
    class MockCollection:
        def __init__(self, name):
            self.name = name
            
        def document(self, doc_id=None):
            return MockDocument(f"{self.name}/{doc_id or 'auto-id'}")
        
        def stream(self):
            return []
    
    class MockDocument:
        def __init__(self, path):
            self.id = path.split('/')[-1]
        
        def set(self, data):
            print(f"❌ MOCK: Would set document with data: {data}")
            print("❌ WARNING: This data is NOT being saved to Firebase!")
        
        def get(self):
            return MockDocumentSnapshot(exists=False)
        
        def delete(self):
            pass
    
    class MockDocumentSnapshot:
        def __init__(self, exists=False):
            self.exists = exists
        
        def to_dict(self):
            return {}
    
    db = MockFirestoreClient()

# Export the database client
__all__ = ['db']