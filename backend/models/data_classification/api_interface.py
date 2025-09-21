"""
API interface for data classification models.
This file acts as a high-level wrapper around the individual classifier and assessor models.
"""
import time
from typing import Dict, List, Any
from pathlib import Path

# Import your underlying model classes with fallback handling
try:
    # Try relative imports first
    from .sensitive_classifier import SensitiveDataClassifier
    from .enhanced_models import DataQualityAssessor
except ImportError:
    try:
        # Try absolute imports as fallback
        from models.data_classification.sensitive_classifier import SensitiveDataClassifier
        from models.data_classification.enhanced_models import DataQualityAssessor
    except ImportError:
        print("Warning: Could not import classification models")
        SensitiveDataClassifier = None
        DataQualityAssessor = None

# Import your logging and metrics utilities with fallback
try:
    from ..utils.logger import setup_logger, ModelMetrics
except ImportError:
    try:
        from models.utils.logger import setup_logger, ModelMetrics
    except ImportError:
        # Fallback logger and metrics
        import logging
        def setup_logger(name):
            return logging.getLogger(name)
        
        class ModelMetrics:
            def __init__(self):
                self.classification_count = 0
                self.quality_assessment_count = 0
                self.error_count = 0
            
            def log_classification(self, processing_time):
                self.classification_count += 1
            
            def log_quality_assessment(self, processing_time):
                self.quality_assessment_count += 1
            
            def log_error(self):
                self.error_count += 1
            
            def get_stats(self):
                return {
                    'total_classifications': self.classification_count,
                    'total_quality_assessments': self.quality_assessment_count,
                    'error_rate': 0.0
                }

# Initialize logger and metrics for this module
logger = setup_logger(__name__)
metrics = ModelMetrics()

class DataClassificationAPI:
    """High-level interface for all data classification and quality services."""
    
    def __init__(self, model_dir: str = None):
        """Initializes all the data governance models."""
        self.model_dir = Path(model_dir) if model_dir else None
        
        # Initialize models if available
        self.sensitive_classifier = None
        self.quality_assessor = None
        
        if SensitiveDataClassifier:
            try:
                self.sensitive_classifier = SensitiveDataClassifier()
                logger.info("Sensitive data classifier initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize sensitive classifier: {e}")
        
        if DataQualityAssessor:
            try:
                self.quality_assessor = DataQualityAssessor()
                logger.info("Data quality assessor initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize quality assessor: {e}")
        
        if self.sensitive_classifier or self.quality_assessor:
            logger.info("Data Classification API initialized successfully.")
        else:
            logger.warning("Data Classification API initialized with no working models.")
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies a string of text for sensitive data patterns.
        This is the primary method called by the orchestrator.
        """
        try:
            start_time = time.time()
            
            if not self.sensitive_classifier:
                return {"error": "Sensitive data classifier not available", "classification": "UNAVAILABLE"}
            
            result = self.sensitive_classifier.classify(text)
            
            processing_time = time.time() - start_time
            metrics.log_classification(processing_time)
            
            logger.info(f"Text classified in {processing_time:.4f}s")
            return result
            
        except Exception as e:
            metrics.log_error()
            logger.error(f"Error in text classification: {str(e)}")
            return {"error": "An internal error occurred during text classification.", "detail": str(e)}
    
    def assess_data_quality(self, data: Dict) -> Dict[str, Any]:
        """
        Assesses the quality of a JSON object (dictionary).
        This is the primary method called by the orchestrator.
        """
        try:
            start_time = time.time()
            
            if not isinstance(data, dict):
                 return {"error": "Input for quality assessment must be a JSON object (dictionary)."}

            if not self.quality_assessor:
                # Fallback simple quality assessment
                total_fields = len(data)
                non_empty_fields = sum(1 for value in data.values() 
                                     if value is not None and str(value).strip())
                completeness_score = non_empty_fields / total_fields if total_fields > 0 else 1.0
                
                return {
                    "overall_score": completeness_score,
                    "completeness": completeness_score,
                    "details": {"total_fields": total_fields, "non_empty_fields": non_empty_fields},
                    "note": "Using fallback quality assessment"
                }

            result = self.quality_assessor.assess_json_quality(data)
            
            processing_time = time.time() - start_time
            metrics.log_quality_assessment(processing_time)
            
            logger.info(f"Data quality assessed in {processing_time:.4f}s")
            return result
            
        except Exception as e:
            metrics.log_error()
            logger.error(f"Error in quality assessment: {str(e)}")
            return {"error": "An internal error occurred during quality assessment.", "detail": str(e)}
    
    def comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """
        Performs a comprehensive analysis on a string of text, returning both a
        sensitivity classification and a simple quality assessment.
        """
        try:
            quality_result = {
                "completeness": 1.0 if text and text.strip() else 0.0,
                "details": "Assessment based on non-empty content of the text string."
            }

            sensitivity_result = self.classify(text)
            
            return {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "sensitivity_analysis": sensitivity_result,
                "quality_assessment": quality_result,
                "recommendations": self._generate_recommendations(sensitivity_result, quality_result)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {"error": "An internal error occurred during comprehensive analysis.", "detail": str(e)}

    def _generate_recommendations(self, sensitivity: Dict, quality: Dict) -> List[str]:
        """Generates simple recommendations based on analysis results."""
        recommendations = []
        
        if quality.get("completeness", 1.0) < 0.8:
            recommendations.append("Address potential empty or missing data issues.")
        
        classification = sensitivity.get("classification", "")
        if classification in ["PII", "Financial", "Secrets", "SENSITIVE"]:
            recommendations.append(f"High sensitivity ({classification}) detected. Implement appropriate security measures like data masking or encryption.")
        
        if not recommendations:
            recommendations.append("Data appears to be of good quality and non-sensitive.")

        return recommendations
    
    def health_check(self) -> Dict[str, Any]:
        """Provides a health status check for the data services."""
        status = {
            "sensitive_classifier": "OK" if self.sensitive_classifier else "UNAVAILABLE",
            "quality_assessor": "OK" if self.quality_assessor else "UNAVAILABLE"
        }
        
        if self.sensitive_classifier and self.quality_assessor:
            return {"status": "OK", "message": "Data classification and quality services are running.", "components": status}
        elif self.sensitive_classifier or self.quality_assessor:
            return {"status": "PARTIAL", "message": "Some data services are running.", "components": status}
        else:
            return {"status": "ERROR", "message": "No data services are available.", "components": status}
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        return metrics.get_stats()