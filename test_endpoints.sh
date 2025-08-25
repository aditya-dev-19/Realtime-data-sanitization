#!/bin/bash

echo "🚀 Starting AI Cybersecurity API Testing..."
echo "=========================================="

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
curl -X GET http://127.0.0.1:8000/
echo -e "\n"

# Test 2: Health check
echo "2. Testing health check..."
curl -X GET http://127.0.0.1:8000/health
echo -e "\n"

# Test 3: Model stats
echo "3. Testing model statistics..."
curl -X GET http://127.0.0.1:8000/model-stats
echo -e "\n"

# Test 4: Dynamic behavior analysis
echo "4. Testing dynamic behavior analysis..."
curl -X POST http://127.0.0.1:8000/analyze-dynamic-behavior \
  -H "Content-Type: application/json" \
  -d '{"call_sequence": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}'
echo -e "\n"

# Test 5: Network traffic analysis
echo "5. Testing network traffic analysis..."
curl -X POST http://127.0.0.1:8000/analyze-network-traffic \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]}'
echo -e "\n"

# Test 6: Sensitive data classification (PII)
echo "6. Testing sensitive data classification (PII)..."
curl -X POST http://127.0.0.1:8000/classify-sensitive-data \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact John Doe at john.doe@example.com or call 555-123-4567"}'
echo -e "\n"

# Test 7: Sensitive data classification (Financial)
echo "7. Testing sensitive data classification (Financial)..."
curl -X POST http://127.0.0.1:8000/classify-sensitive-data \
  -H "Content-Type: application/json" \
  -d '{"text": "My credit card number is 4532-1234-5678-9012"}'
echo -e "\n"

# Test 8: Data quality assessment
echo "8. Testing data quality assessment..."
curl -X POST http://127.0.0.1:8000/assess-data-quality \
  -H "Content-Type: application/json" \
  -d '{"features": [0.8, 0.9, 0.7, 0.85, 0.92]}'
echo -e "\n"

# Test 9: Text analysis
echo "9. Testing text analysis..."
curl -X POST http://127.0.0.1:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Employee ID: 12345, SSN: 123-45-6789, Email: employee@company.com"}'
echo -e "\n"

# Test 10: Comprehensive analysis (Enhanced)
echo "10. Testing comprehensive analysis (Enhanced)..."
curl -X POST http://127.0.0.1:8000/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"text": "API Key: sk-1234567890abcdef, Phone: +1-555-123-4567, URL: https://api.example.com"}'
echo -e "\n"

# Test 11: JSON quality assessment (Enhanced)
echo "11. Testing JSON quality assessment (Enhanced)..."
curl -X POST http://127.0.0.1:8000/assess-json-quality \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30, "city": "New York", "salary": null}'
echo -e "\n"

# Test 12: File analysis
echo "12. Testing file analysis..."
echo "This is a test file with sensitive data: john@example.com and SSN: 123-45-6789" > test_file.txt
curl -X POST http://127.0.0.1:8000/analyze-file -F "file=@test_file.txt"
rm test_file.txt
echo -e "\n"

echo "✅ All endpoint tests completed!"