# Data Classification Models Documentation

## Overview
This module provides comprehensive data classification capabilities including sensitive data detection and data quality assessment.

## Models

### 1. Sensitive Data Classifier
**Purpose**: Detect sensitive information in text data
**Supported Types**: PII, Financial data, Medical information, Secrets/API keys

**Usage**:
```python
from models.data_classification.sensitive_classifier import SensitiveDataClassifier

classifier = SensitiveDataClassifier()
result = classifier.classify("Email: john@example.com, Phone: 555-1234")

# Output format:
{
    "classification": "High",
    "confidence_score": 0.85,
    "detected_types": ["email", "phone"],
    "risk_level": "Medium",
    "recommendations": ["Implement data masking"]
}