"""
Sensitive Data Classifier Module
Detects PII, Financial data, Secrets in text using a hybrid of NLP, regex, and contextual analysis.
"""

import re
import spacy
from typing import Dict, List, Any

class SensitiveDataClassifier:
    """
    Sensitive Data Classifier using NLP and Pattern Matching with de-duplication and contextual logic.
    """
    
    def __init__(self):
        """Initialize the classifier with spaCy model and regex patterns"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.spacy_available = True
        except OSError:
            print("⚠️  spaCy English model not found. Name detection will be disabled.")
            self.nlp = None
            self.spacy_available = False
        
        self.pattern_priority = {
            'credit_card_visa': 1, 'credit_card_mastercard': 1, 'credit_card_amex': 1, 'ssn': 2,
            'credit_card_generic': 3, 'phone': 4, 'api_key': 4, 'password': 4, 'email': 4, 'name': 5, 'bank_account': 6
        }

        self.sensitivity_weights = {
            'ssn': 0.95, 'credit_card_visa': 0.9, 'credit_card_mastercard': 0.9,
            'credit_card_amex': 0.9, 'credit_card_generic': 0.85, 'password': 0.9,
            'api_key': 0.75, 'bank_account': 0.7, 'email': 0.6, 'phone': 0.5, 'name': 0.3
        }

        self.negative_keywords = ['order id', 'tracking number', 'invoice #', 'reference no', 'product id', 'user id', 'serial number']
        self.setup_patterns()
        
    def setup_patterns(self):
        """Setup regex patterns for different data types"""
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.ssn_pattern = re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b')
        self.cc_patterns = {
            'credit_card_generic': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'credit_card_visa': re.compile(r'\b4\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            'credit_card_mastercard': re.compile(r'\b5[1-5]\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            'credit_card_amex': re.compile(r'\b3[47]\d{2}[\s-]?\d{6}[\s-]?\d{5}\b'),
        }
        self.bank_pattern = re.compile(r'\b\d{8,17}\b')
        self.api_key_patterns = [re.compile(r'sk-[A-Za-z0-9]{48}'), re.compile(r'\b[A-Za-z0-9]{32}\b')]
        self.password_pattern = re.compile(r'password\s*[=:]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)

    def _is_context_negative(self, text: str, match_start: int, window: int = 30) -> bool:
        context_text = text[max(0, match_start - window):match_start].lower()
        return any(keyword in context_text for keyword in self.negative_keywords)

    # ===================================================================
    # MODIFIED METHODS: Now adding 'sensitivity_level' to each finding
    # ===================================================================
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        findings = []
        for match in self.email_pattern.finditer(text):
            findings.append({'type': 'email', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['email']})
        
        for match in self.phone_pattern.finditer(text):
            if not self._is_context_negative(text, match.start()):
                findings.append({'type': 'phone', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['phone']})

        for match in self.ssn_pattern.finditer(text):
            findings.append({'type': 'ssn', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['ssn']})
            
        if self.spacy_available and self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    findings.append({'type': 'name', 'value': ent.text, 'start': ent.start_char, 'end': ent.end_char, 'sensitivity_level': self.sensitivity_weights['name']})
        return findings
    
    def detect_financial(self, text: str) -> List[Dict[str, Any]]:
        findings = []
        for card_type, pattern in self.cc_patterns.items():
            for match in pattern.finditer(text):
                if card_type == 'credit_card_generic' and self._is_context_negative(text, match.start()):
                    continue
                findings.append({'type': card_type, 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights[card_type]})
        
        for match in self.bank_pattern.finditer(text):
            if not self._is_context_negative(text, match.start()):
                findings.append({'type': 'bank_account', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['bank_account']})
        return findings
    
    def detect_secrets(self, text: str) -> List[Dict[str, Any]]:
        findings = []
        for pattern in self.api_key_patterns:
            for match in pattern.finditer(text):
                findings.append({'type': 'api_key', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['api_key']})
        for match in self.password_pattern.finditer(text):
            findings.append({'type': 'password', 'value': match.group(), 'start': match.start(), 'end': match.end(), 'sensitivity_level': self.sensitivity_weights['password']})
        return findings

    def _deduplicate_findings(self, all_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not all_findings: return []
        all_findings.sort(key=lambda x: (self.pattern_priority.get(x['type'], 99), -(x['end'] - x['start'])))
        final_findings, covered_ranges = [], []
        for finding in all_findings:
            start, end = finding['start'], finding['end']
            if not any(start < r_end and end > r_start for r_start, r_end in covered_ranges):
                final_findings.append(finding)
                covered_ranges.append((start, end))
        return final_findings
    
    def classify(self, text: str) -> Dict[str, Any]:
        final_findings = self._deduplicate_findings(self.detect_pii(text) + self.detect_financial(text) + self.detect_secrets(text))
        if not final_findings:
            return {'classification': 'Safe', 'sensitivity_level': 0.0, 'details': {}, 'risk_level': 'None', 'summary': 'No sensitive data detected'}
        
        max_sensitivity = max(finding['sensitivity_level'] for finding in final_findings)
        max_finding = max(final_findings, key=lambda x: x['sensitivity_level'])
        
        if max_finding['type'] in ['email', 'phone', 'ssn', 'name']: classification = 'PII'
        elif 'credit_card' in max_finding['type'] or max_finding['type'] == 'bank_account': classification = 'Financial'
        else: classification = 'Secrets'

        pii = [f for f in final_findings if f['type'] in ['email', 'phone', 'ssn', 'name']]
        financial = [f for f in final_findings if 'credit_card' in f['type'] or f['type'] == 'bank_account']
        secrets = [f for f in final_findings if f['type'] in ['api_key', 'password']]
        
        return {
            'classification': classification, 'sensitivity_level': round(max_sensitivity, 2),
            'details': {'pii': {'found': pii, 'types': list(set(f['type'] for f in pii))},
                        'financial': {'found': financial, 'types': list(set(f['type'] for f in financial))},
                        'secrets': {'found': secrets, 'types': list(set(f['type'] for f in secrets))}},
            'risk_level': self._calculate_risk_level(max_sensitivity, classification),
            'summary': self._create_summary({'types': list(set(f['type'] for f in pii))}, {'types': list(set(f['type'] for f in financial))}, {'types': list(set(f['type'] for f in secrets))})
        }
    
    def _calculate_risk_level(self, sensitivity: float, classification: str) -> str:
        if classification == 'Safe': return 'None'
        if sensitivity >= 0.8: return 'High'
        elif sensitivity >= 0.5: return 'Medium'
        else: return 'Low'
    
    def _create_summary(self, pii, financial, secrets) -> str:
        found_types = set(pii['types'] + financial['types'] + secrets['types'])
        return f"Detected: {', '.join(sorted(list(found_types)))}" if found_types else "No sensitive data detected"