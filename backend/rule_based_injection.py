#!/usr/bin/env python3
"""
Rule-based code injection detection as a fallback for the broken ML model.
This provides immediate functionality while the ML model is being retrained.
"""

import re
from typing import Dict, Any

class RuleBasedCodeInjectionDetector:
    """Rule-based code injection detection with configurable thresholds."""

    def __init__(self):
        # Dangerous patterns that indicate code injection
        self.injection_patterns = {
            'xss_patterns': {
                'patterns': [
                    r'<script[^>]*>.*?</script>',
                    r'javascript:',
                    r'on\w+\s*=',
                    r'<iframe[^>]*>.*?</iframe>',
                    r'<object[^>]*>.*?</object>',
                    r'<embed[^>]*>.*?</embed>',
                    r'<form[^>]*>.*?</form>',
                    r'<input[^>]*>',
                    r'<img[^>]*>',
                    r'alert\s*\(',
                    r'prompt\s*\(',
                    r'confirm\s*\(',
                    r'eval\s*\(',
                    r'document\.',
                    r'window\.',
                    r'location\.',
                    r'innerHTML\s*=',
                    r'outerHTML\s*=',
                ],
                'weight': 1.0,
                'severity': 'high'
            },
            'sql_injection_patterns': {
                'patterns': [
                    r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
                    r'\b(OR|AND)\s+[\'"]?\s*\d+\s*=\s*\d+',
                    r'--\s',
                    r'/\*.*?\*/',
                    r'\bUNION\s+SELECT\b',
                    r'\bEXEC\s*\(',
                    r'\bEXECUTE\s*\(',
                    r'\bSP_\w+\s*\(',
                    r'xp_cmdshell',
                    r'OPENROWSET',
                    r'OPENDATASOURCE',
                    r'1=1',
                    r'1=2',
                    r'\'\s*OR\s*\'\d+\'=\'\d+',
                ],
                'weight': 1.0,
                'severity': 'critical'
            },
            'command_injection_patterns': {
                'patterns': [
                    r'\$\([^)]+\)',
                    r'`[^`]+`',
                    r';\s*(ls|cat|rm|cp|mv|wget|curl|ping)',
                    r'\|\s*(ls|cat|rm|cp|mv|wget|curl|ping)',
                    r'&&\s*(ls|cat|rm|cp|mv|wget|curl|ping)',
                    r'\bsudo\b',
                    r'\bsu\b',
                    r'\bchmod\b',
                    r'\bchown\b',
                    r'\bpasswd\b',
                    r'\bssh\b',
                    r'\btelnet\b',
                    r'\bnc\b',
                    r'\bnetcat\b',
                    r'rm\s+-rf',
                    r'format\s+[A-Za-z]:',
                ],
                'weight': 1.0,
                'severity': 'critical'
            },
            'encoding_obfuscation': {
                'patterns': [
                    r'%[0-9A-Fa-f]{2}',  # URL encoding
                    r'&#x[0-9A-Fa-f]+;',  # Hex encoding
                    r'&#\d+;',  # Decimal encoding
                    r'\\\\u[0-9A-Fa-f]{4}',  # Unicode encoding
                    r'\\\\x[0-9A-Fa-f]{2}',  # Hex encoding
                    r'base64',
                    r'rot13',
                    r'encoded',
                    r'obfuscat',
                ],
                'weight': 0.7,
                'severity': 'medium'
            }
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for code injection patterns."""
        text_lower = text.lower()
        score = 0.0
        patterns_found = []
        severity_levels = []

        # Check injection patterns
        for category, config in self.injection_patterns.items():
            category_score = 0.0
            category_patterns = []

            for pattern in config['patterns']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Count occurrences and add to score
                    occurrence_count = len(matches)
                    category_score += (config['weight'] * occurrence_count) / len(config['patterns'])
                    category_patterns.extend([f"{pattern} ({count} times)" for count in [occurrence_count] if count > 0])

            if category_score > 0:
                score += min(category_score, config['weight'])  # Cap at the category weight
                patterns_found.extend(category_patterns)
                severity_levels.append(config.get('severity', 'medium'))

        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))

        # Determine injection type and severity
        max_severity = 'low'
        injection_types = []

        if any('critical' in sev for sev in severity_levels):
            max_severity = 'critical'
            injection_types.extend(['Command Injection', 'SQL Injection'])
        elif any('high' in sev for sev in severity_levels):
            max_severity = 'high'
            injection_types.extend(['XSS', 'SQL Injection'])
        elif score > 0.5:
            max_severity = 'medium'
            injection_types.append('Potential Code Injection')

        # Determine if it's injection - lowered threshold for better detection
        is_injection = score > 0.1  # Lowered threshold from 0.3 to 0.1

        return {
            "status": "Injection" if is_injection else "Safe",
            "confidence": score,
            "details": {
                "score": score,
                "patterns_found": patterns_found,
                "severity": max_severity,
                "injection_types": injection_types,
                "analysis_method": "Rule-based detection"
            }
        }

def test_rule_based_injection_detector():
    """Test the rule-based injection detector with various examples."""
    detector = RuleBasedCodeInjectionDetector()

    test_cases = [
        {
            "name": "XSS Attack",
            "text": "<script>alert('XSS')</script>",
            "expected": "Injection"
        },
        {
            "name": "SQL Injection",
            "text": "SELECT * FROM users WHERE id = 1 OR 1=1 --",
            "expected": "Injection"
        },
        {
            "name": "Command Injection",
            "text": "; rm -rf /",
            "expected": "Injection"
        },
        {
            "name": "Safe HTML",
            "text": "<html><body><h1>Hello World</h1></body></html>",
            "expected": "Safe"
        },
        {
            "name": "Normal Text",
            "text": "This is a normal message about programming and development.",
            "expected": "Safe"
        },
        {
            "name": "Mixed Attack",
            "text": "<script>alert('XSS')</script> UNION SELECT password FROM users --",
            "expected": "Injection"
        }
    ]

    print("🧪 Testing Rule-Based Code Injection Detector")
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
        print(f"   Details: {result['details']['patterns_found'][:2]}...")  # Show first 2 patterns
        print()

    print("=" * 60)
    print(f"📊 Results: {correct_predictions}/{total_tests} correct ({correct_predictions/total_tests*100:.1f}%)")

    if correct_predictions == total_tests:
        print("🎉 Rule-based injection detector is working perfectly!")
        return True
    else:
        print(f"⚠️ {total_tests - correct_predictions} test(s) failed.")
        return False

if __name__ == "__main__":
    test_rule_based_injection_detector()
