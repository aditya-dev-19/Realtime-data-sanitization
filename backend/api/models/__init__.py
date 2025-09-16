# This module initializes all models and makes them available for import
# Note: We avoid direct imports here to prevent circular imports

# This makes the models available when importing from models package directly
__all__ = ['Alert', 'AlertSeverity', 'AlertStatus', 'AlertType', 'AnalysisResult']

# Lazy imports to avoid circular imports
import sys
from typing import Any

# Cache for lazy-loaded modules
_import_cache = {}

def __getattr__(name: str) -> Any:
    if name in _import_cache:
        return _import_cache[name]
        
    if name == 'Alert':
        from .alert import Alert as _Alert
        _import_cache['Alert'] = _Alert
        return _Alert
        
    elif name in ('AlertSeverity', 'AlertStatus', 'AlertType'):
        from .alert import AlertSeverity, AlertStatus, AlertType
        _import_cache['AlertSeverity'] = AlertSeverity
        _import_cache['AlertStatus'] = AlertStatus
        _import_cache['AlertType'] = AlertType
        return _import_cache[name]
        
    elif name == 'AnalysisResult':
        from .analysis_result import AnalysisResult as _AnalysisResult
        _import_cache['AnalysisResult'] = _AnalysisResult
        return _AnalysisResult
        
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
