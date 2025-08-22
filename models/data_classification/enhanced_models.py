"""
Enhanced Models for Data Classification
File: models/data_classification/enhanced_models.py
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DetectedPattern:
    """Data class for detected sensitive patterns"""
    type: str
    value: str
    confidence: float
    position: Tuple[int, int]
    category: str

@dataclass
class QualityAssessment:
    """Data class for quality assessment results"""
    overall_score: float
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    details: Dict[str, Any]

class EnhancedSensitiveClassifier:
    """
    Enhanced classifier for sensitive data detection with improved patterns
    """
    
    def __init__(self):
        """Initialize the enhanced classifier"""
        self.patterns = self._initialize_patterns()
        self.confidence_threshold = 0.5
        logger.info("Enhanced Sensitive Classifier initialized")
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize detection patterns with confidence weights"""
        return {
            'email': {
                'pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'confidence': 0.95,
                'category': 'PII'
            },
            'phone_us': {
                'pattern': re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
                'confidence': 0.90,
                'category': 'PII'
            },
            'ssn': {
                'pattern': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
                'confidence': 0.98,
                'category': 'PII'
            },
            'credit_card': {
                'pattern': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
                'confidence': 0.85,
                'category': 'FINANCIAL'
            },
            'ip_address': {
                'pattern': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
                'confidence': 0.80,
                'category': 'TECHNICAL'
            },
            'url': {
                'pattern': re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'),
                'confidence': 0.75,
                'category': 'TECHNICAL'
            }
        }
    
    def classify_text(self, text: str, return_patterns: bool = True) -> Dict[str, Any]:
        """
        Classify text for sensitive data with enhanced detection
        """
        if not isinstance(text, str):
            return {'error': 'Input must be a string', 'classification': 'ERROR'}
        
        detected_patterns = []
        max_confidence = 0.0
        
        # Detect patterns
        for pattern_name, pattern_info in self.patterns.items():
            matches = list(pattern_info['pattern'].finditer(text))
            
            for match in matches:
                detected_pattern = DetectedPattern(
                    type=pattern_name,
                    value=match.group(),
                    confidence=pattern_info['confidence'],
                    position=(match.start(), match.end()),
                    category=pattern_info['category']
                )
                detected_patterns.append(detected_pattern)
                max_confidence = max(max_confidence, pattern_info['confidence'])
        
        # Determine classification
        if detected_patterns:
            classification = 'SENSITIVE'
            confidence = min(max_confidence + 0.1, 1.0)
        else:
            classification = 'NON_SENSITIVE'
            confidence = 0.9
        
        result = {
            'classification': classification,
            'confidence': confidence,
            'text_length': len(text),
            'patterns_found': len(detected_patterns)
        }
        
        if return_patterns:
            result['detected_patterns'] = [
                {
                    'type': p.type,
                    'category': p.category,
                    'confidence': p.confidence,
                    'position': p.position
                } for p in detected_patterns
            ]
        
        return result
    
    def get_pattern_info(self) -> Dict[str, List[str]]:
        """Get information about supported patterns"""
        pattern_info = {}
        for name, info in self.patterns.items():
            if info['category'] not in pattern_info:
                pattern_info[info['category']] = []
            pattern_info[info['category']].append(name)
        return pattern_info


class DataQualityAssessor:
    """
    Assess data quality across multiple dimensions
    """
    
    def __init__(self):
        """Initialize the quality assessor"""
        logger.info("Data Quality Assessor initialized")
    
    def assess_json_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess quality of JSON-like data
        """
        if not isinstance(data, dict):
            return {
                'error': 'Input must be a dictionary',
                'overall_score': 0.0
            }
        
        # Simple quality assessment
        total_fields = len(data)
        non_empty_fields = sum(1 for value in data.values() 
                              if value is not None and str(value).strip())
        
        completeness_score = non_empty_fields / total_fields if total_fields > 0 else 1.0
        
        return {
            'overall_score': completeness_score,
            'completeness': completeness_score,
            'details': {
                'total_fields': total_fields,
                'non_empty_fields': non_empty_fields
            },
            'assessment_time': datetime.now().isoformat()
        }


if __name__ == "__main__":
    print("🧪 Testing Enhanced Models")
    
    # Test Enhanced Classifier
    classifier = EnhancedSensitiveClassifier()
    test_text = "Contact John at john.doe@example.com"
    
    result = classifier.classify_text(test_text)
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print("✅ Enhanced models working!")
