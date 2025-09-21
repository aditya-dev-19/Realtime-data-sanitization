# Updated firebase_admin.py with proper error handling
# Replace your backend/api/firebase_admin.py with this content

import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- Initialize Firebase Admin SDK ---
# This setup is crucial for connecting to your Firestore database.

try:
    # Get project ID from environment variable or use default
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'realtime-data-sanitization')  # Replace with your actual project ID
    
    # Initialize the app if not already initialized
    try:
        app = firebase_admin.get_app()
        print("✅ Firebase app already initialized")
    except ValueError:
        # Try to initialize with explicit project ID
        try:
            # Try with service account file if available
            service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {'projectId': project_id})
                print(f"✅ Firebase initialized with service account for project: {project_id}")
            else:
                # Initialize with project ID only (for local development)
                firebase_admin.initialize_app(options={'projectId': project_id})
                print(f"✅ Firebase initialized with project ID: {project_id}")
                
        except Exception as init_error:
            print(f"❌ Firebase initialization failed: {init_error}")
            print("⚠️  Firebase features will be disabled")
            raise

    # Get Firestore client with explicit project ID
    db = firestore.client(project=project_id)
    print("✅ Firestore client initialized successfully")

except Exception as e:
    print(f"❌ Firebase/Firestore setup failed: {e}")
    print("⚠️  Creating mock database client for development")
    
    # Create a mock database client that doesn't crash the app
    class MockFirestoreClient:
        def collection(self, name):
            return MockCollection()
        
        def document(self, path):
            return MockDocument()
    
    class MockCollection:
        def document(self, doc_id=None):
            return MockDocument()
        
        def add(self, data):
            print(f"Mock: Would add document with data: {data}")
            return (MockDocument(), "mock_doc_id")
        
        def stream(self):
            return []
        
        def order_by(self, field, **kwargs):
            return self
        
        def limit(self, count):
            return self
    
    class MockDocument:
        def __init__(self):
            self.id = "mock_document_id"
        
        def set(self, data):
            print(f"Mock: Would set document data: {data}")
        
        def update(self, data):
            print(f"Mock: Would update document with: {data}")
        
        def get(self):
            return MockDocumentSnapshot()
        
        def delete(self):
            print("Mock: Would delete document")
    
    class MockDocumentSnapshot:
        def __init__(self):
            self.exists = False
        
        def to_dict(self):
            return {}
    
    # Use mock client
    db = MockFirestoreClient()
    print("⚠️  Using mock Firestore client - data will not persist!")