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
            print("   To enable full functionality, install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            self.spacy_available = False
        
        # Priority map for de-duplicating overlapping findings
        self.pattern_priority = {
            'credit_card_visa': 1, 'credit_card_mastercard': 1, 'credit_card_amex': 1,
            'ssn': 2,
            'credit_card_generic': 3,
            'phone': 4,
            'api_key': 4, 'password': 4, 'email': 4,
            'name': 5,
            'bank_account': 6 # Lowest priority
        }

        # NEW: List of keywords that indicate a number is NOT sensitive
        self.negative_keywords = [
            'order id', 'tracking number', 'invoice #', 'reference no', 
            'product id', 'user id', 'serial number'
        ]
        
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
        self.api_key_patterns = [
            re.compile(r'sk-[A-Za-z0-9]{48}'),
            re.compile(r'\b[A-Za-z0-9]{32}\b'),
        ]
        self.password_pattern = re.compile(r'password\s*[=:]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)

    # NEW: Context checking helper function
    def _is_context_negative(self, text: str, match_start: int, window: int = 30) -> bool:
        """Checks the text before a match for negative keywords."""
        start_pos = max(0, match_start - window)
        context_text = text[start_pos:match_start].lower()
        for keyword in self.negative_keywords:
            if keyword in context_text:
                return True
        return False

    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII and return a list of findings with positions."""
        findings = []
        for match in self.email_pattern.finditer(text):
            findings.append({'type': 'email', 'value': match.group(), 'start': match.start(), 'end': match.end()})
        
        # MODIFIED: Added context check for phone numbers
        for match in self.phone_pattern.finditer(text):
            if not self._is_context_negative(text, match.start()):
                findings.append({'type': 'phone', 'value': match.group(), 'start': match.start(), 'end': match.end()})

        for match in self.ssn_pattern.finditer(text):
            findings.append({'type': 'ssn', 'value': match.group(), 'start': match.start(), 'end': match.end()})
            
        # Only use spaCy if available
        if self.spacy_available and self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    findings.append({'type': 'name', 'value': ent.text, 'start': ent.start_char, 'end': ent.end_char})
        return findings
    
    def detect_financial(self, text: str) -> List[Dict[str, Any]]:
        """Detect financial info and return a list of findings with positions."""
        findings = []
        for card_type, pattern in self.cc_patterns.items():
            for match in pattern.finditer(text):
                # MODIFIED: Context check for generic cards
                if card_type == 'credit_card_generic' and self._is_context_negative(text, match.start()):
                    continue
                findings.append({'type': card_type, 'value': match.group(), 'start': match.start(), 'end': match.end()})
        
        # MODIFIED: Added context check for bank accounts
        for match in self.bank_pattern.finditer(text):
            if not self._is_context_negative(text, match.start()):
                findings.append({'type': 'bank_account', 'value': match.group(), 'start': match.start(), 'end': match.end()})
        return findings
    
    def detect_secrets(self, text: str) -> List[Dict[str, Any]]:
        """Detect secrets and return a list of findings with positions."""
        findings = []
        for pattern in self.api_key_patterns:
            for match in pattern.finditer(text):
                findings.append({'type': 'api_key', 'value': match.group(), 'start': match.start(), 'end': match.end()})
        for match in self.password_pattern.finditer(text):
            findings.append({'type': 'password', 'value': match.group(), 'start': match.start(), 'end': match.end()})
        return findings

    def _deduplicate_findings(self, all_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """De-duplicates findings based on position and priority."""
        if not all_findings:
            return []
        
        all_findings.sort(key=lambda x: (self.pattern_priority.get(x['type'], 99), -(x['end'] - x['start'])))
        
        final_findings = []
        covered_ranges = []

        for finding in all_findings:
            start, end = finding['start'], finding['end']
            is_covered = False
            for r_start, r_end in covered_ranges:
                if start < r_end and end > r_start:
                    is_covered = True
                    break
            if not is_covered:
                final_findings.append(finding)
                covered_ranges.append((start, end))
                
        return final_findings
    
    def classify(self, text: str) -> Dict[str, Any]:
        """Main classification method with de-duplication and context checks."""
        pii_findings = self.detect_pii(text)
        financial_findings = self.detect_financial(text)
        secrets_findings = self.detect_secrets(text)
        
        all_findings_raw = pii_findings + financial_findings + secrets_findings
        final_findings = self._deduplicate_findings(all_findings_raw)
        
        pii_results = {'found': [f for f in final_findings if f['type'] in ['email', 'phone', 'ssn', 'name']], 'types': []}
        financial_results = {'found': [f for f in final_findings if 'credit_card' in f['type'] or f['type'] == 'bank_account'], 'types': []}
        secrets_results = {'found': [f for f in final_findings if f['type'] in ['api_key', 'password']], 'types': []}
        
        pii_results['types'] = list(set(f['type'] for f in pii_results['found']))
        financial_results['types'] = list(set('credit_card' if 'credit_card' in f['type'] else f['type'] for f in financial_results['found']))
        secrets_results['types'] = list(set(f['type'] for f in secrets_results['found']))
        
        pii_results['confidence'] = min(len(pii_results['found']) * 0.3, 1.0)
        financial_results['confidence'] = min(len(financial_results['found']) * 0.4, 1.0)
        secrets_results['confidence'] = min(len(secrets_results['found']) * 0.5, 1.0)

        confidences = {
            'PII': pii_results['confidence'],
            'Financial': financial_results['confidence'],
            'Secrets': secrets_results['confidence']
        }
        
        if not any(confidences.values()):
            max_category = 'Safe'
        else:
            max_category = max(confidences, key=confidences.get)
        max_confidence = confidences.get(max_category, 0)
        
        if max_confidence < 0.2:
            classification = 'Safe'
            confidence = 1.0 - max_confidence
        else:
            classification = max_category
            confidence = max_confidence
            
        return {
            'classification': classification,
            'confidence': confidence,
            'details': {
                'pii': pii_results,
                'financial': financial_results,
                'secrets': secrets_results
            },
            'risk_level': self._calculate_risk_level(confidence, classification),
            'summary': self._create_summary(pii_results, financial_results, secrets_results)
        }
    
    def _calculate_risk_level(self, confidence: float, classification: str) -> str:
        """Calculate risk level based on confidence"""
        if classification == 'Safe':
            return 'None'
        if confidence >= 0.8:
            return 'High'
        elif confidence >= 0.5:
            return 'Medium'
        else:
            return 'Low'
    
    def _create_summary(self, pii, financial, secrets) -> str:
        """Create a human-readable summary"""
        found_types = set(pii['types'] + financial['types'] + secrets['types'])
        if not found_types:
            return "No sensitive data detected"
        else:
            return f"Detected: {', '.join(sorted(list(found_types)))}"
    
    def predict(self, texts):
        """Predict method for compatibility with orchestrator"""
        if isinstance(texts, str):
            texts = [texts]
        
        results = []
        for text in texts:
            classification_result = self.classify(text)
            results.append(classification_result['classification'])
        
        return results
