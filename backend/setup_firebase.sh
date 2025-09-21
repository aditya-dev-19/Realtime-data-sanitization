#!/bin/bash
# Cloud Run Firebase Configuration Script
# Run this script to properly configure Firebase authentication for your Cloud Run service

set -e

PROJECT_ID="realtime-data-sanitization"
SERVICE_NAME="cybersecurity-api-service"
REGION="us-central1"
SERVICE_ACCOUNT_NAME="firebase-admin-sa"

echo "🔧 Configuring Firebase Authentication for Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"

# 1. Create a dedicated service account for Firebase Admin
echo "📋 Step 1: Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="Firebase Admin Service Account" \
    --description="Service account for Firebase Admin SDK in Cloud Run" \
    --project=$PROJECT_ID || echo "Service account might already exist"

# 2. Grant necessary roles to the service account
echo "🔑 Step 2: Granting Firebase roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/firebase.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/firebase.sdkAdminServiceAgent"

# 3. Enable required APIs
echo "🚀 Step 3: Enabling required APIs..."
gcloud services enable firestore.googleapis.com --project=$PROJECT_ID
gcloud services enable firebase.googleapis.com --project=$PROJECT_ID
gcloud services enable identitytoolkit.googleapis.com --project=$PROJECT_ID

# 4. Update Cloud Run service to use the new service account
echo "⚡ Step 4: Updating Cloud Run service..."
gcloud run services update $SERVICE_NAME \
    --service-account="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --region=$REGION \
    --project=$PROJECT_ID

# Also update the Cloud Build trigger to use correct service account
echo "🔨 Updating Cloud Build service account permissions..."
CLOUD_BUILD_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@cloudbuild.gserviceaccount.com
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${CLOUD_BUILD_SA}" \
    --role="roles/run.admin"

# 5. Set environment variables
echo "🔧 Step 5: Setting environment variables..."
gcloud run services update $SERVICE_NAME \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars="FIREBASE_PROJECT_ID=${PROJECT_ID}" \
    --region=$REGION \
    --project=$PROJECT_ID

echo "✅ Configuration complete!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy your updated code with the new firebase_admin.py"
echo "2. Check the Cloud Run logs to verify Firebase initialization"
echo "3. Test user registration and login"
echo ""
echo "🔍 To check the service account configuration:"
echo "gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "🔍 To check logs:"
echo "gcloud logs read --project=$PROJECT_ID --filter='resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\"' --limit=50"