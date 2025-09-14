import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def load_sample_data(data_type: str = "mixed") -> pd.DataFrame:
    """Load sample data for testing"""
    # Your data generation functions here
    pass

def validate_input_data(data: Any) -> bool:
    """Validate input data format"""
    if isinstance(data, str):
        return len(data.strip()) > 0
    elif isinstance(data, pd.DataFrame):
        return not data.empty
    return False

def format_results(sensitivity_result: Dict, quality_result: Dict) -> Dict:
    """Format final results for API response"""
    return {
        "timestamp": pd.Timestamp.now().isoformat(),
        "sensitivity_analysis": sensitivity_result,
        "quality_assessment": quality_result,
        "overall_risk_score": calculate_risk_score(sensitivity_result, quality_result)
    }

def calculate_risk_score(sensitivity: Dict, quality: Dict) -> float:
    """Calculate overall risk score"""
    sensitivity_weight = 0.7
    quality_weight = 0.3
    
    # Extract risk from sensitivity (higher sensitivity = higher risk)
    sensitivity_risk = 1.0 if sensitivity.get("classification") == "Highly Sensitive" else 0.5
    
    # Extract risk from quality (lower quality = higher risk)
    quality_risk = 1.0 - quality.get("overall_score", 0.5)
    
    return sensitivity_weight * sensitivity_risk + quality_weight * quality_risk