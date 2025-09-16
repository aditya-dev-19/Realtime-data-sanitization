# In backend/api/firebase_admin.py
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
# The SDK will automatically use the project's service account credentials
# when running in a Google Cloud environment like Cloud Run.
firebase_admin.initialize_app()

db = firestore.client()