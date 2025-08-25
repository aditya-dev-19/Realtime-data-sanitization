"""
Configuration settings for data classification models
"""

class ClassifierConfig:
    """Configuration for Sensitive Data Classifier"""
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    
    # Pattern matching settings
    ENABLE_FUZZY_MATCHING = True
    FUZZY_MATCH_THRESHOLD = 0.85
    
    # Performance settings
    MAX_TEXT_LENGTH = 50000  # Maximum characters to process
    BATCH_SIZE = 1000  # For batch processing
    
    # Classification categories
    SENSITIVITY_LEVELS = {
        'Safe': 0,
        'Low': 1,
        'Medium': 2,
        'High': 3,
        'Critical': 4
    }

class QualityConfig:
    """Configuration for Data Quality Assessor"""
    
    # Quality score weights
    COMPLETENESS_WEIGHT = 0.3
    CONSISTENCY_WEIGHT = 0.25
    ACCURACY_WEIGHT = 0.25
    UNIQUENESS_WEIGHT = 0.2
    
    # Thresholds
    MISSING_DATA_THRESHOLD = 0.1  # 10% missing data threshold
    OUTLIER_THRESHOLD = 3  # Standard deviations for outlier detection
    
    # Quality categories
    QUALITY_LEVELS = {
        'Excellent': (0.9, 1.0),
        'Good': (0.7, 0.9),
        'Fair': (0.5, 0.7),
        'Poor': (0.3, 0.5),
        'Critical': (0.0, 0.3)
    }