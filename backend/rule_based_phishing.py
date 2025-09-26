#!/usr/bin/env python3
"""
Rule-based phishing detection as a fallback for the broken ML model.
This provides immediate functionality while the ML model is being retrained.
"""

import re
from typing import Dict, Any
from urllib.parse import urlparse

class RuleBasedPhishingDetector:
    """Rule-based phishing detection with configurable thresholds."""

    def __init__(self):
        # Phishing indicators with weights
        self.phishing_indicators = {
            'urgent_keywords': {
                'keywords': [
                    'urgent', 'immediate', 'important', 'attention', 'warning',
                    'alert', 'suspicious', 'compromised', 'breached', 'hacked',
                    'security', 'verify', 'confirm', 'validate', 
                    'login', 'password', 'update', 'required', 'necessary',
                    'critical', 'emergency', 'action', 'required'
                ],
                'weight': 0.8  # Increased weight
            },
            'suspicious_urls': {
                'patterns': [
                    r'http://[^\.]+\.[^\.]+\.[^\.]+',  # Unusual domain structure
                    r'https?://[^\s]+\.com[^\s]*',     # Generic .com domains
                    r'https?://[^\s]*login[^\s]*',     # Login-related URLs
                    r'https?://[^\s]*secure[^\s]*',    # Fake secure sites
                    r'https?://[^\s]*bank[^\s]*',      # Bank-related URLs
                    r'https?://[^\s]*account[^\s]*',   # Account-related URLs
                    r'https?://[^\s]*verify[^\s]*',    # Verification URLs
                    r'https?://[^\s]*update[^\s]*',    # Update URLs
                    r'https?://[^\s]*claim[^\s]*',     # Claim URLs
                    r'https?://[^\s]*prize[^\s]*',     # Prize URLs
                ],
                'weight': 1.2  # Increased weight slightly
            },
            'suspicious_tlds': {
                'tlds': ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.info', '.biz'],
                'weight': 0.5  # Increased weight
            },
            'suspicious_content': {
                'patterns': [
                    r'account.*suspend', r'account.*close', r'account.*terminat',
                    r'password.*expir', r'login.*fail', r'payment.*declin',
                    r'card.*expir', r'security.*breach', r'unauthorized.*access',
                    r'click.*link', r'don.*t.*delay', r'act.*now', r'immediate.*action'
                ],
                'weight': 1.0  # Increased weight
            }
        }

        # Safe indicators (negative weights) - increased power to prevent false positives
        self.safe_indicators = {
            'personal_names': {
                'patterns': [r'my name is', r'i am', r'hello.*my name', r'hi.*i am'],
                'weight': -0.5  # Increased from -0.2
            },
            'normal_greetings': {
                'patterns': [r'hello', r'hi', r'good morning', r'good afternoon', r'good evening'],
                'weight': -0.3  # Increased from -0.1
            },
            'normal_content': {
                'patterns': [r'technical', r'programming', r'code', r'development', r'project', r'engineer', r'software'],
                'weight': -0.4  # Increased from -0.1
            }
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for phishing indicators."""
        text_lower = text.lower()
        score = 0.0
        indicators_found = []

        # Check phishing indicators
        for category, config in self.phishing_indicators.items():
            category_score = 0.0
            category_indicators = []

            if 'keywords' in config:
                for keyword in config['keywords']:
                    if keyword in text_lower:
                        category_score += config['weight'] / len(config['keywords'])
                        category_indicators.append(f"Keyword: '{keyword}'")

            if 'patterns' in config:
                for pattern in config['patterns']:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        category_score += config['weight'] / len(config['patterns'])
                        category_indicators.append(f"Pattern: '{pattern}'")

            if 'tlds' in config:
                for tld in config['tlds']:
                    if tld in text_lower:
                        category_score += config['weight'] / len(config['tlds'])
                        category_indicators.append(f"Suspicious TLD: '{tld}'")

            if category_score > 0:
                score += category_score
                indicators_found.extend(category_indicators)

        # Check safe indicators (subtract from score)
        for category, config in self.safe_indicators.items():
            category_score = 0.0

            if 'patterns' in config:
                for pattern in config['patterns']:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        category_score += config['weight'] / len(config['patterns'])

            if category_score < 0:
                score += category_score  # Subtract from total score

        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))

        # Determine if it's phishing - balanced threshold
        is_phishing = score > 0.25  # Balanced threshold - catches most phishing, avoids false positives

        return {
            "status": "Phishing" if is_phishing else "Safe",
            "confidence": score,
            "details": {
                "score": score,
                "indicators_found": indicators_found,
                "analysis_method": "Rule-based detection"
            }
        }

def test_rule_based_detector():
    """Test the rule-based detector with various examples."""
    detector = RuleBasedPhishingDetector()

    test_cases = [
        {
            "name": "Obvious Phishing",
            "text": "URGENT: Your account has been compromised! Click here immediately to verify: http://secure-bank-login.com/verify Account Number: 1234-5678-9012-3456 If you don't act now, your account will be suspended!",
            "expected": "Phishing"
        },
        {
            "name": "Safe Text",
            "text": "Hello, my name is John and I work as a software engineer. I enjoy reading technical books and writing clean code.",
            "expected": "Safe"
        },
        {
            "name": "Suspicious URL",
            "text": "Click here to claim your prize: http://suspicious-site.com/claim",
            "expected": "Phishing"
        },
        {
            "name": "Normal Email",
            "text": "Hi, please find the attached document for your review. Best regards, John.",
            "expected": "Safe"
        },
        {
            "name": "Banking Scam",
            "text": "Your bank account has been frozen. Please login immediately to verify your identity: https://secure-bank-verification.com/login",
            "expected": "Phishing"
        },
        {
            "name": "Technical Discussion",
            "text": "I'm working on a new Python project for data analysis. The code uses pandas and numpy for processing large datasets.",
            "expected": "Safe"
        }
    ]

    print("🧪 Testing Rule-Based Phishing Detector")
    print("=" * 60)

    correct_predictions = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        result = detector.analyze(test_case["text"])
        prediction = result["status"]
        confidence = result["confidence"]
        expected = test_case["expected"]

        is_correct = prediction == expected
        if is_correct:
            correct_predictions += 1

        status = "✅" if is_correct else "❌"
        print(f"{status} Test {i}: {test_case['name']}")
        print(f"   Expected: {expected}, Got: {prediction}")
        print(f"   Confidence: {confidence:.4f}")
        print(f"   Details: {result['details']['indicators_found'][:3]}...")  # Show first 3 indicators
        print()

    print("=" * 60)
    print(f"📊 Results: {correct_predictions}/{total_tests} correct ({correct_predictions/total_tests*100:.1f}%)")

    if correct_predictions == total_tests:
        print("🎉 Rule-based detector is working perfectly!")
        return True
    else:
        print(f"⚠️ {total_tests - correct_predictions} test(s) failed.")
        return False

if __name__ == "__main__":
    test_rule_based_detector()
