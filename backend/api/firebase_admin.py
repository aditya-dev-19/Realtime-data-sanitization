import firebase_admin
from firebase_admin import credentials, firestore

# --- Initialize Firebase Admin SDK ---
# This setup is crucial for connecting to your Firestore database.
# When your app runs on Google Cloud (like Cloud Run), it will automatically
# use the project's default service account for authentication.
# When you run it locally, it uses the credentials you set up with 'gcloud auth application-default login'.

try:
    # Initialize the app. If it's already initialized, this will not raise an error.
    app = firebase_admin.get_app()
except ValueError:
    # If the app is not initialized, initialize it.
    firebase_admin.initialize_app()

# Get a client that can interact with the Firestore database.
# This 'db' object is what your other files (like alerts.py and users.py) will import and use.
db = firestore.client()

print("✅ Firebase Admin SDK initialized successfully.")