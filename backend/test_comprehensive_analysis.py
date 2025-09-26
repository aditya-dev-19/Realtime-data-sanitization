#!/usr/bin/env python3
"""
Comprehensive Test Script for the /comprehensive-analysis endpoint

This script tests the comprehensive analysis API endpoint to ensure:
- All model artifacts are working properly
- Response structure is correct
- Different types of content are analyzed appropriately
- File uploads work correctly
- Error handling is functioning

Usage:
    python test_comprehensive_analysis.py
"""

import requests
import json
import time
from typing import Dict, Any
import os

class ComprehensiveAnalysisTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/comprehensive-analysis"
        self.test_results = []

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test results for reporting"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if response_data:
            result["response"] = response_data

        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")

    def test_basic_connectivity(self) -> bool:
        """Test 1: Basic connectivity to the endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test_result("Basic Connectivity", True, f"Health check passed: {response.json()}")
                return True
            else:
                self.log_test_result("Basic Connectivity", False, f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_text_analysis_phishing(self) -> bool:
        """Test 2: Text analysis with phishing content"""
        test_text = """
        URGENT: Your account has been compromised!
        Click here immediately to verify your account: http://secure-bank-login.com/verify
        Account Number: 1234-5678-9012-3456
        If you don't act now, your account will be suspended!
        """

        try:
            response = requests.post(
                self.endpoint,
                data={"text": test_text},
                timeout=30
            )

            if response.status_code != 200:
                self.log_test_result("Text Analysis - Phishing", False, f"Status code: {response.status_code}")
                return False

            data = response.json()

            # Check required fields
            required_fields = [
                "analysis_type", "overall_risk_score", "risk_level",
                "model_artifacts_used", "results", "timestamp"
            ]

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test_result("Text Analysis - Phishing", False, f"Missing fields: {missing_fields}")
                return False

            # Check model artifacts
            model_artifacts = data.get("model_artifacts_used", {})
            if not any(model_artifacts.values()):
                self.log_test_result("Text Analysis - Phishing", False, "No model artifacts were used")
                return False

            # Check results structure
            results = data.get("results", {})
            expected_analyses = ["sensitive_data", "phishing", "code_injection", "data_quality"]

            for analysis in expected_analyses:
                if analysis not in results:
                    self.log_test_result("Text Analysis - Phishing", False, f"Missing analysis: {analysis}")
                    return False

            # Check for phishing detection
            phishing_result = results.get("phishing", {})
            if phishing_result.get("status") != "Phishing":
                self.log_test_result("Text Analysis - Phishing", False, f"Expected phishing detection, got: {phishing_result.get('status')}")
                return False

            # Check for sensitive data detection
            sensitive_result = results.get("sensitive_data", {})
            if sensitive_result.get("classification") == "UNKNOWN":
                self.log_test_result("Text Analysis - Phishing", False, "Sensitive data not detected in phishing text")
                return False

            self.log_test_result(
                "Text Analysis - Phishing",
                True,
                f"Risk Score: {data.get('overall_risk_score', 0):.2f}, "
                f"Phishing: {phishing_result.get('status')}, "
                f"Sensitive: {sensitive_result.get('classification')}"
            )
            return True

        except Exception as e:
            self.log_test_result("Text Analysis - Phishing", False, f"Exception: {str(e)}")
            return False

    def test_text_analysis_clean(self) -> bool:
        """Test 3: Text analysis with clean content"""
        test_text = """
        Hello, my name is John Doe and I work as a software engineer.
        I enjoy reading technical books and writing clean code.
        My favorite programming languages are Python and JavaScript.
        """

        try:
            response = requests.post(
                self.endpoint,
                data={"text": test_text},
                timeout=30
            )

            if response.status_code != 200:
                self.log_test_result("Text Analysis - Clean", False, f"Status code: {response.status_code}")
                return False

            data = response.json()

            # Check risk score should be low for clean text
            risk_score = data.get("overall_risk_score", 1.0)
            if risk_score > 0.3:
                self.log_test_result("Text Analysis - Clean", False, f"Risk score too high for clean text: {risk_score}")
                return False

            # Check phishing should be safe
            phishing_result = data.get("results", {}).get("phishing", {})
            if phishing_result.get("status") == "Phishing":
                self.log_test_result("Text Analysis - Clean", False, "Clean text flagged as phishing")
                return False

            self.log_test_result(
                "Text Analysis - Clean",
                True,
                f"Risk Score: {risk_score:.2f}, "
                f"Phishing: {phishing_result.get('status', 'Unknown')}"
            )
            return True

        except Exception as e:
            self.log_test_result("Text Analysis - Clean", False, f"Exception: {str(e)}")
            return False

    def test_file_analysis(self) -> bool:
        """Test 4: File analysis with a test file"""
        # Create a test file with sensitive and suspicious content
        test_content = """
        This is a test file with sensitive information.

        Email: test@example.com
        Phone: +1-555-0123
        SSN: 123-45-6789

        URGENT: Please click this link to verify: http://suspicious-site.com/verify
        Your account will be suspended if you don't act now!

        Also, here's some code: <script>alert('XSS')</script>
        """

        try:
            # Create multipart request with file
            files = {
                'file': ('test_file.txt', test_content, 'text/plain')
            }

            response = requests.post(
                self.endpoint,
                files=files,
                timeout=30
            )

            if response.status_code != 200:
                self.log_test_result("File Analysis", False, f"Status code: {response.status_code}")
                return False

            data = response.json()

            # Check file metadata is included
            file_metadata = data.get("file_metadata", {})
            if not file_metadata:
                self.log_test_result("File Analysis", False, "File metadata missing")
                return False

            # Check file analysis results
            file_analysis = data.get("results", {}).get("file_analysis", {})
            if not file_analysis:
                self.log_test_result("File Analysis", False, "File analysis missing")
                return False

            # Check alerts were created
            alerts_created = data.get("alerts_created", [])
            if not alerts_created:
                self.log_test_result("File Analysis", False, "No alerts created for suspicious file")
                return False

            self.log_test_result(
                "File Analysis",
                True,
                f"File: {file_metadata.get('filename')}, "
                f"Size: {file_metadata.get('size')} bytes, "
                f"Alerts: {len(alerts_created)}, "
                f"Risk Score: {data.get('overall_risk_score', 0):.2f}"
            )
            return True

        except Exception as e:
            self.log_test_result("File Analysis", False, f"Exception: {str(e)}")
            return False

    def test_model_availability(self) -> bool:
        """Test 5: Check if all model artifacts are available"""
        try:
            response = requests.get(f"{self.base_url}/model-stats", timeout=10)

            if response.status_code != 200:
                self.log_test_result("Model Availability", False, f"Status code: {response.status_code}")
                return False

            model_stats = response.json()

            # Check if we have model information
            if not model_stats:
                self.log_test_result("Model Availability", False, "No model stats returned")
                return False

            self.log_test_result("Model Availability", True, f"Model stats retrieved: {len(model_stats)} entries")
            return True

        except Exception as e:
            self.log_test_result("Model Availability", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests and provide summary"""
        print("🔍 Starting Comprehensive Analysis API Tests")
        print("=" * 60)

        tests = [
            self.test_basic_connectivity,
            self.test_model_availability,
            self.test_text_analysis_phishing,
            self.test_text_analysis_clean,
            self.test_file_analysis,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1
            print()

        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("🎉 All tests passed! Comprehensive analysis is working properly.")
        else:
            print(f"⚠️ {total-passed} test(s) failed. Check the details above.")

        return passed == total

    def print_detailed_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 60)
        print("📋 DETAILED TEST RESULTS")
        print("=" * 60)

        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"\n{status}: {result['test_name']}")
            print(f"   Time: {result['timestamp']}")
            if result["details"]:
                print(f"   Details: {result['details']}")
            if not result["success"] and "response" in result:
                print(f"   Response: {json.dumps(result['response'], indent=2)}")


def main():
    """Main function to run the tests"""
    tester = ComprehensiveAnalysisTester()

    success = tester.run_all_tests()

    if not success:
        tester.print_detailed_results()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
