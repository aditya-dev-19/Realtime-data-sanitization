#!/bin/bash
# Test Firebase Configuration After Service Update

PROJECT_ID="realtime-data-sanitization"
SERVICE_NAME="cybersecurity-api-service"
REGION="us-central1"
SERVICE_URL="https://cybersecurity-api-service-44185828496.us-central1.run.app"

echo "🧪 Testing Firebase Configuration"
echo "================================"

# 1. Check service configuration
echo "📋 Step 1: Checking Cloud Run service configuration..."
gcloud run services describe $SERVICE_NAME --region=$REGION --format="yaml" | grep -A 5 -B 5 "serviceAccountName\|env"

echo ""
echo "📋 Service URL: $SERVICE_URL"

# 2. Test the health endpoint
echo ""
echo "🔍 Step 2: Testing health endpoint..."
curl -X GET "$SERVICE_URL/health" -H "Content-Type: application/json" | python3 -m json.tool || echo "Health endpoint test failed"

# 3. Test user registration
echo ""
echo "👤 Step 3: Testing user registration..."
TEST_EMAIL="test_$(date +%s)@example.com"
REGISTER_RESPONSE=$(curl -s -X POST "$SERVICE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"testpass123\"}")

echo "Registration response: $REGISTER_RESPONSE"

# 4. Test user login with the same credentials
echo ""
echo "🔑 Step 4: Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$SERVICE_URL/token" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"testpass123\"}")

echo "Login response: $LOGIN_RESPONSE"

# 5. Check recent logs for Firebase initialization
echo ""
echo "📜 Step 5: Checking recent logs for Firebase initialization..."
echo "Looking for Firebase initialization messages..."
gcloud logs read --project=$PROJECT_ID \
  --filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\"" \
  --limit=10 \
  --format="value(textPayload)" | grep -i "firebase\|firestore\|mock"

echo ""
echo "🔍 Full recent logs (last 5):"
gcloud logs read --project=$PROJECT_ID \
  --filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\"" \
  --limit=5 \
  --format="table(timestamp,textPayload)"

echo ""
echo "📋 Test Summary:"
echo "==============="
echo "1. Service URL: $SERVICE_URL"
echo "2. Test email: $TEST_EMAIL"
echo "3. Check the logs above for 'Firebase initialized' messages"
echo "4. If you see 'Mock:' messages, Firebase is still not working"
echo "5. If you see 'Firebase initialized with Application Default Credentials', it's working!"

echo ""
echo "🔧 If Firebase is still not working:"
echo "1. Update your backend/api/firebase_admin.py with the new code"
echo "2. Commit and push: git add ., git commit -m 'Update Firebase config', git push"
echo "3. Wait for automatic deployment"
echo "4. Run this test again"