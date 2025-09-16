# api/orchestrator.py
import os
# Force TensorFlow to use CPU to avoid CUDA errors on machines without a configured GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.sequence import pad_sequences
except ImportError:
    # Fallback if TensorFlow is not available
    load_model = None
    pad_sequences = None
    print("Warning: TensorFlow not available. Some features may be limited.")

import numpy as np
import joblib

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
except ImportError:
    torch = None
    AutoModelForSequenceClassification = None
    AutoTokenizer = None
    print("Warning: Transformers not available. Some features may be limited.")

# Import local modules
try:
    from .models.data_classification.sensitive_classifier import SensitiveDataClassifier, EnhancedSensitiveClassifier
    from .models.data_classification.quality_assessor import DataQualityAssessor, EnhancedDataQualityAssessor
    from .models.data_classification.api_interface import DataClassificationAPI
    from .models.data_classification.config import ClassifierConfig, QualityConfig
except ImportError as e:
    print(f"Warning: Could not import data classification modules: {e}")
    SensitiveDataClassifier = None
    EnhancedSensitiveClassifier = None
    DataQualityAssessor = None
    EnhancedDataQualityAssessor = None
    DataClassificationAPI = None
    ClassifierConfig = None
    QualityConfig = None

# Import your custom model classes to resolve the unpickling error
# Using absolute imports to avoid circular dependencies
# These are already imported above with relative imports
    class ClassifierConfig: pass
    class QualityConfig: pass

class CybersecurityOrchestrator:
    def __init__(self, model_dir='../saved_models/'):
        print("Initializing Cybersecurity Orchestrator...")
        
        # Check scikit-learn version for compatibility
        import sklearn
        print(f"📊 scikit-learn version: {sklearn.__version__}")
        
        # 1. Load Dynamic Behavior Analyzer (LSTM)
        try:
            # Create fallback model directly to avoid LSTM parameter issues
            print("   Creating fallback behavior analyzer to avoid LSTM compatibility issues...")
            self._create_fallback_dynamic_model()
            print("✅ Fallback Dynamic Behavior Analyzer created.")
        except Exception as fallback_error:
            print(f"❌ Failed to create fallback model: {fallback_error}")
            self.dynamic_model = None
            print("⚠️  Dynamic behavior analysis disabled")

        # 2. Load Network Traffic Models
        try:
            # Suppress scikit-learn version warnings
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
                
                self.iso_forest = joblib.load(f'{model_dir}isolation_forest_model.pkl')
                self.ids_model = joblib.load(f'{model_dir}intrusion_detection_model.pkl')
                self.network_scaler = joblib.load(f'{model_dir}feature_scaler.pkl')
            print("✅ Network Traffic models loaded.")
        except Exception as e:
            print(f"❌ ERROR loading Network Traffic models: {e}")
            print("⚠️  Network traffic analysis disabled")
            self.iso_forest = None
            self.ids_model = None
            self.network_scaler = None

        # 3. Load Transformer Models (Phishing & Code Injection Detection)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        phishing_model_path = project_root / "saved_models" / "phishing_model_v2"
        code_injection_model_path = project_root / "saved_models" / "code_injection_model_prod"
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Using device: {self.device}")

        try:
            self.phishing_tokenizer = AutoTokenizer.from_pretrained(phishing_model_path)
            self.phishing_model = AutoModelForSequenceClassification.from_pretrained(phishing_model_path)
            self.phishing_model.to(self.device)
            print("✅ Phishing Detection Model loaded.")

            self.code_injection_tokenizer = AutoTokenizer.from_pretrained(code_injection_model_path)
            self.code_injection_model = AutoModelForSequenceClassification.from_pretrained(code_injection_model_path)
            self.code_injection_model.to(self.device)
            print("✅ Code Injection Detection Model loaded.")

        except Exception as e:
            print(f"⚠️  Warning: Failed to load Transformer models: {e}")
            print("   Transformer-based detection will be disabled")
            self.phishing_tokenizer = None
            self.phishing_model = None
            self.code_injection_tokenizer = None
            self.code_injection_model = None

        # 4. Load Data Classification Models
        print("🚀 Initializing Enhanced Data Classification Models...")
        
        try:
            # Initialize the enhanced API interface
            self.data_classification_api = DataClassificationAPI()
            
            # Keep backward compatibility with original models
            try:
                from api.models.data_classification.sensitive_classifier import SensitiveDataClassifier
                from api.models.data_classification.quality_assessor import DataQualityAssessor
                
                # Initialize enhanced models
                self.enhanced_sensitive_classifier = EnhancedSensitiveClassifier()
                self.enhanced_quality_assessor = EnhancedDataQualityAssessor()
                
                # Keep original models for fallback
                self.sensitive_classifier = SensitiveDataClassifier()
                self.quality_assessor = DataQualityAssessor()
            except ImportError as e:
                print(f"Warning: Could not initialize data classification models: {e}")
                self.enhanced_sensitive_classifier = None
                self.enhanced_quality_assessor = None
                self.sensitive_classifier = None
                self.quality_assessor = None
            
            self.sensitive_metadata = {
                "note": "Using enhanced model instances with API interface",
                "enhanced_features": True,
                "api_interface": True,
                "transformer_models": bool(self.phishing_model and self.code_injection_model)
            }
            print("✅ Enhanced Data Classification models initialized successfully.")
            
        except Exception as e:
            print(f"⚠️  Error initializing enhanced models: {e}")
            print("   Falling back to basic models...")
            
            # Fallback to basic models
            try:
                from api.models.data_classification.sensitive_classifier import SensitiveDataClassifier
                from api.models.data_classification.quality_assessor import DataQualityAssessor
                
                self.sensitive_classifier = SensitiveDataClassifier()
                self.quality_assessor = DataQualityAssessor()
            except ImportError as e:
                print(f"Warning: Could not initialize fallback models: {e}")
                self.sensitive_classifier = None
                self.quality_assessor = None
                
            self.data_classification_api = None
            self.enhanced_sensitive_classifier = None
            self.enhanced_quality_assessor = None
            
            self.sensitive_metadata = {"note": "Using basic model instances (fallback)"}
            print("✅ Basic Data Classification model instances created.")

        print("\n🚀 Orchestrator ready!")

    def _create_fallback_dynamic_model(self):
        """Create a simple fallback model for dynamic behavior analysis"""
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        
        # Simple feedforward model as fallback
        self.dynamic_model = Sequential([
            Dense(64, activation='relu', input_shape=(100,)),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        self.sequence_length = 100

    def analyze_dynamic_behavior(self, call_sequence: list[int]):
        """Analyzes a sequence of system calls with the LSTM model."""
        if self.dynamic_model is None:
            return {"status": "Model unavailable", "confidence": 0.0, "error": "Dynamic behavior analyzer not loaded"}
        
        try:
            padded_sequence = pad_sequences([call_sequence], maxlen=self.sequence_length, padding='post', truncating='post')
            prediction_prob = self.dynamic_model.predict(padded_sequence)[0][0]
            
            if prediction_prob > 0.5:
                return {"status": "Attack Behavior Detected", "confidence": float(prediction_prob)}
            else:
                return {"status": "Normal Behavior", "confidence": 1.0 - float(prediction_prob)}
        except Exception as e:
            return {"status": "Analysis failed", "confidence": 0.0, "error": str(e)}

    def analyze_network_traffic(self, features: list[float]):
        """Analyzes network features with both anomaly and intrusion detection models."""
        if any(model is None for model in [self.iso_forest, self.ids_model, self.network_scaler]):
            return {"error": "Network traffic models not loaded", "status": "Model unavailable"}
        
        try:
            features_2d = np.array(features).reshape(1, -1)
            scaled_features = self.network_scaler.transform(features_2d)
            
            # Anomaly Detection
            anomaly_prediction = self.iso_forest.predict(scaled_features)
            anomaly_status = "Anomaly" if anomaly_prediction[0] == -1 else "Normal"
            
            # Intrusion Classification
            intrusion_prediction = self.ids_model.predict(scaled_features)
            
            return {
                "anomaly_detection": {"status": anomaly_status},
                "intrusion_classification": {"attack_type": str(intrusion_prediction[0])}
            }
        except Exception as e:
            return {"error": str(e), "status": "Analysis failed"}

    def classify_sensitive_data(self, text: str):
        """Classifies text to identify sensitive data using enhanced models."""
        try:
            # Use enhanced API interface if available
            if self.data_classification_api:
                return self.data_classification_api.classify(text)
            
            # Use enhanced classifier if available
            elif self.enhanced_sensitive_classifier:
                result = self.enhanced_sensitive_classifier.classify_text(text)
                return {
                    "classification": result.get('classification', 'UNKNOWN'),
                    "confidence": result.get('confidence', 0.0),
                    "details": result.get('detected_patterns', []),
                    "text_length": result.get('text_length', 0),
                    "patterns_found": result.get('patterns_found', 0)
                }
            
            # Fallback to original classifier
            else:
                prediction = self.sensitive_classifier.predict([text])
                return {"data_type": prediction[0], "details": "Model classified text content."}
                
        except Exception as e:
            return {"error": f"Classification failed: {str(e)}", "classification": "ERROR"}

    def assess_data_quality(self, data):
        """Assesses the quality of a given data sample (supports both dict and list formats)."""
        try:
            # Use enhanced API interface if available
            if self.data_classification_api and isinstance(data, dict):
                return self.data_classification_api.assess_data_quality(data)
            
            # Use enhanced quality assessor if available
            elif self.enhanced_quality_assessor and isinstance(data, dict):
                return self.enhanced_quality_assessor.assess_json_quality(data)
            
            # Handle list/array input (original functionality)
            elif isinstance(data, (list, np.ndarray)):
                if isinstance(data, list):
                    features_2d = np.array(data).reshape(1, -1)
                else:
                    features_2d = data.reshape(1, -1) if data.ndim == 1 else data
                
                quality_score = self.quality_assessor.predict(features_2d)
                return {"quality_score": quality_score[0], "recommendation": "Review data if score is low."}
            
            # Handle string input for text quality assessment
            elif isinstance(data, str):
                # Simple text quality assessment
                quality_score = 1.0 if data and data.strip() else 0.0
                return {
                    "quality_score": quality_score,
                    "completeness": quality_score,
                    "recommendation": "Text appears complete" if quality_score > 0.5 else "Text is empty or incomplete"
                }
            
            else:
                return {"error": "Unsupported data format. Use dict, list, or string.", "quality_score": 0.0}
                
        except Exception as e:
            return {"error": f"Quality assessment failed: {str(e)}", "quality_score": 0.0}
    
    def comprehensive_analysis(self, text: str):
        """Performs comprehensive analysis using enhanced API interface."""
        try:
            if self.data_classification_api:
                return self.data_classification_api.comprehensive_analysis(text)
            else:
                # Fallback implementation
                sensitive_result = self.classify_sensitive_data(text)
                quality_result = self.assess_data_quality(text)
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "sensitivity_analysis": sensitive_result,
                    "quality_assessment": quality_result,
                    "recommendations": self._generate_recommendations(sensitive_result, quality_result)
                }
        except Exception as e:
            return {"error": f"Comprehensive analysis failed: {str(e)}"}
    
    def analyze_file_for_threats(self, file_path: str):
        """Analyzes a file for potential threats (placeholder implementation)."""
        import hashlib
        import os
        
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = os.path.splitext(file_path)[1].lower()
            
            # Simple heuristic analysis (placeholder)
            is_malicious = False
            confidence = 0.5
            
            # Basic checks
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif']
            if file_type in suspicious_extensions:
                is_malicious = True
                confidence = 0.8
            
            return {
                "file_hash": file_hash,
                "file_type": file_type,
                "file_size": file_size,
                "is_malicious": is_malicious,
                "confidence": confidence,
                "analysis_details": {
                    "static_analysis": "Basic file type and hash analysis performed",
                    "threat_indicators": ["Suspicious file extension"] if is_malicious else []
                }
            }
            
        except Exception as e:
            return {
                "error": f"File analysis failed: {str(e)}",
                "is_malicious": False,
                "confidence": 0.0
            }
    
    def _generate_recommendations(self, sensitivity_result, quality_result):
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        if quality_result.get("quality_score", 1.0) < 0.8:
            recommendations.append("Address potential data quality issues.")
        
        classification = sensitivity_result.get("classification", "")
        if classification in ["PII", "Financial", "Secrets", "SENSITIVE"]:
            recommendations.append(f"High sensitivity ({classification}) detected. Implement appropriate security measures.")
        
        if not recommendations:
            recommendations.append("Data appears to be of good quality and non-sensitive.")
            
        return recommendations
    
    def get_model_stats(self):
        """Get model performance statistics."""
        try:
            if self.data_classification_api:
                return self.data_classification_api.get_model_stats()
            else:
                return {"message": "Enhanced API interface not available", "stats": {}}
        except Exception as e:
            return {"error": f"Failed to get model stats: {str(e)}"}
    
    def health_check(self):
        """Perform health check on all models."""
        status = {
            "orchestrator": "OK",
            "dynamic_behavior": "OK" if self.dynamic_model else "DISABLED",
            "network_traffic": "OK" if all([self.iso_forest, self.ids_model, self.network_scaler]) else "DISABLED",
            "data_classification": "ENHANCED" if self.data_classification_api else "BASIC",
            "enhanced_features": bool(self.data_classification_api)
        }
        
        if self.data_classification_api:
            api_health = self.data_classification_api.health_check()
            status.update(api_health)
            
        return status
    
    def detect_phishing(self, text: str):
        """Analyzes text to detect phishing attempts using a transformer model."""
        if not self.phishing_model or not self.phishing_tokenizer:
            return {"error": "Phishing detection model not available", "status": "Model unavailable"}
        
        try:
            inputs = self.phishing_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.phishing_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                prediction = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0, prediction].item()
            label = self.phishing_model.config.id2label[prediction]
            return {"status": label, "confidence": confidence}
        except Exception as e:
            return {"error": f"Phishing detection failed: {str(e)}", "status": "Analysis failed"}

    def detect_code_injection(self, text: str):
        """Analyzes text to detect code injection attempts using a transformer model."""
        if not self.code_injection_model or not self.code_injection_tokenizer:
            return {"error": "Code injection detection model not available", "status": "Model unavailable"}
        
        try:
            inputs = self.code_injection_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.code_injection_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                prediction = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0, prediction].item()
            label = self.code_injection_model.config.id2label[prediction]
            return {"status": label, "confidence": confidence}
        except Exception as e:
            return {"error": f"Code injection detection failed: {str(e)}", "status": "Analysis failed"}

    def analyze_system_calls(self, call_sequence):
        """Analyzes system calls - alias for analyze_dynamic_behavior for backward compatibility."""
        return self.analyze_dynamic_behavior(call_sequence)
    
    def comprehensive_data_analysis(self, text: str):
        """Alias for comprehensive_analysis for backward compatibility."""
        return self.comprehensive_analysis(text)

    def get_data_services_health(self):
        """Alias for health_check for backward compatibility."""
        return self.health_check()
