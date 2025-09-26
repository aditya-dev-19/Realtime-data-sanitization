#!/bin/bash
# Quick curl-based tests for comprehensive analysis endpoint

BASE_URL="https://cybersecurity-api-service-44185828496.us-central1.run.app"
ENDPOINT="$BASE_URL/comprehensive-analysis"

echo "🔍 Quick Comprehensive Analysis Tests"
echo "===================================="

# Test 1: Basic connectivity
echo -e "\n1️⃣ Testing basic connectivity..."
curl -s "$BASE_URL/health" | jq . 2>/dev/null || echo "Health check response received"

# Test 2: Text analysis with phishing content
echo -e "\n2️⃣ Testing phishing text analysis..."
curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=URGENT: Click here to verify your account: http://phishing-site.com/verify Your account will be suspended!" \
  | jq '.analysis_type, .overall_risk_score, .risk_level, (.results.phishing.status // "N/A")' 2>/dev/null

# Test 3: Clean text analysis
echo -e "\n3️⃣ Testing clean text analysis..."
curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Hello, my name is John. I am a software engineer who enjoys coding." \
  | jq '.overall_risk_score, .risk_level, (.results.phishing.status // "N/A")' 2>/dev/null

# Test 4: File analysis
echo -e "\n4️⃣ Testing file analysis..."
echo "This is a test file with sensitive data.
Email: test@example.com
Phone: 123-456-7890
URGENT: Click here: http://suspicious-site.com" > test_file.txt

curl -s -X POST "$ENDPOINT" \
  -F "file=@test_file.txt" \
  | jq '.analysis_type, .overall_risk_score, .risk_level, (.file_metadata.filename // "N/A"), (.alerts_created | length)' 2>/dev/null

rm -f test_file.txt

# Test 5: Model stats
echo -e "\n5️⃣ Checking model availability..."
curl -s "$BASE_URL/model-stats" | jq '. | keys' 2>/dev/null || echo "Model stats endpoint accessible"

echo -e "\n✅ Quick tests completed!"
echo "💡 For detailed testing, run: python test_comprehensive_analysis.py"
