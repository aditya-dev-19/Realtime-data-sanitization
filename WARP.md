# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an AI-powered cybersecurity threat detection system that combines multiple machine learning models to analyze various types of cyber threats. The project consists of a Python FastAPI backend and a Flutter mobile frontend for real-time data sanitization.

### Architecture

The system follows a **modular microservice architecture**:
- **FastAPI Backend**: Central orchestrator managing multiple AI models
- **CybersecurityOrchestrator**: Core class that coordinates all ML models
- **Model Components**: Specialized models for different threat types
- **GCS Integration**: Models stored in Google Cloud Storage buckets
- **Firebase**: Authentication and data persistence
- **Flutter Frontend**: Cross-platform mobile application

### Key Components

1. **CybersecurityOrchestrator** (`backend/api/orchestrator.py`): The central hub that loads and manages all ML models, providing a unified interface for threat analysis.

2. **ML Models Portfolio**:
   - Dynamic Behavior Analysis (LSTM-based)
   - Network Traffic Analysis (Isolation Forest + Random Forest)
   - Transformer Models (Phishing & Code Injection Detection)
   - Sensitive Data Classification
   - Data Quality Assessment
   - File Threat Analysis

3. **API Layer** (`backend/api/main.py`): FastAPI application with comprehensive endpoints for different analysis types, automatic model downloading from GCS, and centralized alerting system.

## Development Commands

### Backend Development

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_orchestrator.py
python test_models.py
python test_alerts.py
python test_alerts_endpoint.py

# Quick test of specific components
python quick_test.py
```

### Frontend Development

```bash
# Navigate to Flutter app directory
cd frontend/realtime_datasanitization

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Build for release
flutter build apk
flutter build ios
```

### Testing & Validation

```bash
# Test orchestrator functionality
cd backend && python test_orchestrator.py

# Test individual models
python test_models.py

# Test API endpoints
python test_alerts_endpoint.py

# Create test models if missing
python api/create_test_models.py
```

### Model Management

```bash
# Fix/update GCS models
python fix_gcs_model.py

# Deploy API to cloud
python deploy_api.py

# Simple model fixes
python simple_model_fix.py
```

## Project Structure

```
ai_cybersecurity_project/
├── backend/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # Main API with all endpoints
│   │   ├── orchestrator.py    # Central ML orchestrator
│   │   ├── alerting.py        # Centralized alerting system
│   │   ├── firebase_admin.py  # Firebase integration
│   │   └── schemas.py         # Pydantic models
│   ├── models/                # ML model components
│   │   ├── file_analyzer.py   # File threat analysis
│   │   ├── text_analyzer.py   # Text analysis models
│   │   └── user.py           # User management
│   ├── notebooks/             # Jupyter notebooks for model development
│   └── test_*.py             # Test scripts
├── frontend/
│   └── realtime_datasanitization/  # Flutter mobile app
│       ├── lib/              # Dart source code
│       ├── android/          # Android-specific files
│       ├── ios/             # iOS-specific files
│       └── pubspec.yaml     # Flutter dependencies
└── .venv/                   # Python virtual environment
```

## Key Architectural Patterns

### Orchestrator Pattern
The `CybersecurityOrchestrator` class acts as a facade that:
- Loads all ML models from a centralized directory
- Provides graceful fallbacks when models are unavailable
- Handles different ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Offers a unified API for threat analysis

### Model Loading Strategy
- Models are downloaded from GCS buckets at startup
- Fallback models are created if original models are missing
- Conditional imports prevent crashes from missing dependencies
- Each model type has specific preprocessing pipelines

### Alert System
Centralized alerting (`alerting.py`) that:
- Creates standardized alert formats
- Integrates with Firebase for persistence
- Triggers on various threat detection events
- Supports different alert severity levels

## API Endpoints

The FastAPI backend exposes these key endpoints:

- `POST /analyze-dynamic-behavior` - System call sequence analysis
- `POST /analyze-network-traffic` - Network anomaly detection (expects 10 features)
- `POST /analyze-text` - Text analysis for sensitive data and quality
- `POST /analyze-file` - File upload and malware analysis
- `POST /detect-phishing` - Phishing email/URL detection
- `POST /detect-code-injection` - SQL/code injection detection
- `POST /classify-sensitive-data` - PII and sensitive data classification
- `POST /comprehensive-analysis` - Multi-model analysis pipeline
- `GET /health` - System health check

## Development Guidelines

### Model Integration
When adding new ML models:
1. Add model loading logic to `CybersecurityOrchestrator`
2. Implement graceful fallbacks in `_load_model()` helper
3. Add preprocessing methods for the specific model type
4. Create corresponding API endpoint in `main.py`
5. Add alerting logic for threat detection events

### Testing Strategy
- Use the provided test scripts (`test_*.py`) for component validation
- The `test_orchestrator.py` script provides comprehensive testing
- Create test models automatically if GCS models are unavailable
- Flutter app testing uses standard `flutter test` commands

### Environment Setup
The system expects:
- Python 3.12+ environment with all dependencies installed
- Google Cloud credentials for GCS access
- Firebase configuration for authentication
- Flutter SDK for mobile development

### Model Storage Convention
- Models are stored in GCS bucket: `realtime-data-sanitization-models`
- Local models directory: `downloaded_models/` or `saved_models/`
- Expected model files include: `isolation_forest_model.pkl`, `intrusion_detection_model.pkl`, `feature_scaler.pkl`

## Deployment Notes

- API is designed for cloud deployment (Google Cloud Run)
- Models are automatically downloaded from GCS at startup
- Health checks validate both database and model availability
- Flutter app supports cross-platform deployment (Android/iOS)

## Live API
Production API: https://cybersecurity-api-service-44185828496.us-central1.run.app/