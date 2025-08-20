"""
API interface for data classification models.
This file acts as a high-level wrapper around the individual classifier and assessor models.
"""
import time
from typing import Dict, List, Any

# Import your underlying model classes
from .sensitive_classifier import SensitiveDataClassifier
from .enhanced_models import DataQualityAssessor 

# Import your logging and metrics utilities
from ..utils.logger import setup_logger, ModelMetrics

# Initialize logger and metrics for this module
logger = setup_logger(__name__)
metrics = ModelMetrics()

class DataClassificationAPI:
    """High-level interface for all data classification and quality services."""
    
    def __init__(self):
        """Initializes all the data governance models."""
        self.sensitive_classifier = SensitiveDataClassifier()
        self.quality_assessor = DataQualityAssessor()
        logger.info("Data Classification API initialized successfully.")
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies a string of text for sensitive data patterns.
        This is the primary method called by the orchestrator.
        """
        try:
            start_time = time.time()
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
        
        if sensitivity.get("classification") in ["PII", "Financial", "Secrets"]:
            recommendations.append(f"High sensitivity ({sensitivity.get('classification')}) detected. Implement appropriate security measures like data masking or encryption.")
        
        if not recommendations:
            recommendations.append("Data appears to be of good quality and non-sensitive.")

        return recommendations
    
    def health_check(self) -> Dict[str, Any]:
        """Provides a health status check for the data services."""
        if self.sensitive_classifier and self.quality_assessor:
            return {"status": "OK", "message": "Data classification and quality services are running."}
        else:
            return {"status": "ERROR", "message": "One or more data services failed to initialize."}
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        return metrics.get_stats()