#!/bin/bash

# Base URL for your API (mapped host port -> container port)
BASE_URL="http://127.0.0.1:9090"

echo "🚀 Starting AI Cybersecurity API Testing against $BASE_URL ..."
echo "============================================================="

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
curl -s -X GET "$BASE_URL/" | jq .
echo -e "\n"

# Test 2: Health check
echo "2. Testing health check..."
curl -s -X GET "$BASE_URL/health" | jq .
echo -e "\n"

# Test 3: Model stats
echo "3. Testing model statistics..."
curl -s -X GET "$BASE_URL/model-stats" | jq .
echo -e "\n"

# Test 4: Dynamic behavior analysis
echo "4. Testing dynamic behavior analysis..."
curl -s -X POST "$BASE_URL/analyze-dynamic-behavior" \
  -H "Content-Type: application/json" \
  -d '{"call_sequence": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}' | jq .
echo -e "\n"

# Test 5: Network traffic analysis
echo "5. Testing network traffic analysis..."
curl -s -X POST "$BASE_URL/analyze-network-traffic" \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]}' | jq .
echo -e "\n"

# Test 6: Sensitive data classification (PII)
echo "6. Testing sensitive data classification (PII)..."
curl -s -X POST "$BASE_URL/classify-sensitive-data" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact John Doe at john.doe@example.com or call 555-123-4567"}' | jq .
echo -e "\n"

# Test 7: Sensitive data classification (Financial)
echo "7. Testing sensitive data classification (Financial)..."
curl -s -X POST "$BASE_URL/classify-sensitive-data" \
  -H "Content-Type: application/json" \
  -d '{"text": "My credit card number is 4532-1234-5678-9012"}' | jq .
echo -e "\n"

# Test 8: Data quality assessment
echo "8. Testing data quality assessment..."
curl -s -X POST "$BASE_URL/assess-data-quality" \
  -H "Content-Type: application/json" \
  -d '{"features": [0.8, 0.9, 0.7, 0.85, 0.92]}' | jq .
echo -e "\n"

# Test 9: Text analysis
echo "9. Testing text analysis..."
curl -s -X POST "$BASE_URL/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Employee ID: 12345, SSN: 123-45-6789, Email: employee@company.com"}' | jq .
echo -e "\n"

# Test 10: Comprehensive analysis (Enhanced)
echo "10. Testing comprehensive analysis (Enhanced)..."
curl -s -X POST "$BASE_URL/comprehensive-analysis" \
  -H "Content-Type: application/json" \
  -d '{"text": "API Key: sk-1234567890abcdef, Phone: +1-555-123-4567, URL: https://api.example.com"}' | jq .
echo -e "\n"

# Test 11: JSON quality assessment (Enhanced)
echo "11. Testing JSON quality assessment (Enhanced)..."
curl -s -X POST "$BASE_URL/assess-json-quality" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "John Doe", "email": "john@example.com", "age": 30, "city": "New York", "salary": null}}' | jq .
echo -e "\n"

# Test 12: File analysis
echo "12. Testing file analysis..."
echo "This is a test file with sensitive data: john@example.com and SSN: 123-45-6789" > test_file.txt
curl -s -X POST "$BASE_URL/analyze-file" -F "file=@test_file.txt" | jq .
rm test_file.txt
echo -e "\n"

echo "✅ All endpoint tests completed!"
