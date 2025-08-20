"""
Logging utilities for data classification models
"""
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
    """Setup logger with proper formatting"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if in local environment)
    try:
        log_dir = '/content/data_classification_project/logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/classification_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        pass  # Skip file logging in restricted environments
    
    return logger

class ModelMetrics:
    """Track model performance metrics"""
    
    def __init__(self):
        self.classification_count = 0
        self.quality_assessment_count = 0
        self.processing_times = []
        self.error_count = 0
    
    def log_classification(self, processing_time: float):
        self.classification_count += 1
        self.processing_times.append(processing_time)
    
    def log_quality_assessment(self, processing_time: float):
        self.quality_assessment_count += 1
        self.processing_times.append(processing_time)
    
    def log_error(self):
        self.error_count += 1
    
    def get_stats(self):
        return {
            'total_classifications': self.classification_count,
            'total_quality_assessments': self.quality_assessment_count,
            'avg_processing_time': sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            'error_rate': self.error_count / (self.classification_count + self.quality_assessment_count) if (self.classification_count + self.quality_assessment_count) > 0 else 0
        }