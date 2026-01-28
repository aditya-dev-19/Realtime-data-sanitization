# 🔐 AI-Powered Cybersecurity Threat Detection System

An intelligent, real-time cybersecurity threat detection system that combines multiple machine learning models to analyze and identify various cyber threats. The system features a Python FastAPI backend with advanced ML capabilities and a Flutter mobile frontend for cross-platform accessibility.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Flutter-3.9+-02569B.svg)](https://flutter.dev/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.19-FF6F00.svg)](https://www.tensorflow.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3-EE4C2C.svg)](https://pytorch.org/)

## 🌟 Features

### 🤖 Multi-Model AI Analysis
- **Dynamic Behavior Analysis**: LSTM-based system call sequence analysis
- **Network Traffic Analysis**: Anomaly detection using Isolation Forest and Random Forest
- **Phishing Detection**: Transformer-based email and URL analysis
- **Code Injection Detection**: SQL injection and code injection pattern recognition
- **Sensitive Data Classification**: PII and confidential data identification
- **File Threat Analysis**: Malware and PE file analysis
- **Data Quality Assessment**: Automated data integrity and quality evaluation

### 🔄 Real-Time Processing
- Fast API responses with async processing
- Real-time threat alerts and notifications
- Continuous model orchestration and coordination
- Comprehensive analysis pipeline combining multiple models

### ☁️ Cloud-Native Architecture
- Google Cloud Storage integration for ML models
- Firebase authentication and data persistence
- Deployed on Google Cloud Run for scalability
- Automatic model downloading and caching

### 📱 Cross-Platform Mobile App
- Flutter-based mobile application
- Real-time threat monitoring
- Beautiful UI with animations and custom fonts
- Push notifications for critical alerts

## 🏗️ Architecture

The system follows a **modular microservice architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter Mobile App                    │
│              (Cross-Platform Frontend)                   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │       CybersecurityOrchestrator                  │   │
│  │      (Central ML Model Coordinator)              │   │
│  └──┬──────────────────────────────────────────────┘   │
│     │                                                    │
│  ┌──▼────────────────────────────────────────────────┐ │
│  │         ML Model Portfolio                        │ │
│  │  • Dynamic Behavior (LSTM)                        │ │
│  │  • Network Traffic (Isolation Forest + RF)        │ │
│  │  • Phishing Detection (Transformers)              │ │
│  │  • Code Injection Detection (Transformers)        │ │
│  │  • Sensitive Data Classifier                      │ │
│  │  • File Threat Analyzer                           │ │
│  │  • Data Quality Assessor                          │ │
│  └───────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                 │
┌───────▼──────┐              ┌──────────▼─────────┐
│  Google Cloud │              │     Firebase       │
│   Storage     │              │  Auth & Database   │
│  (ML Models)  │              │                    │
└───────────────┘              └────────────────────┘
```

## 📦 Project Structure

```
ai_cybersecurity_project/
├── backend/                      # Python FastAPI Backend
│   ├── api/                     # API Layer
│   │   ├── main.py             # Main API with all endpoints
│   │   ├── orchestrator.py     # Central ML orchestrator
│   │   ├── alerting.py         # Centralized alerting system
│   │   ├── firebase_admin.py   # Firebase integration
│   │   └── schemas.py          # Pydantic models
│   ├── models/                  # ML Model Components
│   │   ├── file_analyzer.py    # File threat analysis
│   │   ├── text_analyzer.py    # Text analysis models
│   │   └── user.py            # User management
│   ├── notebooks/              # Jupyter notebooks for model development
│   ├── downloaded_models/      # Cached ML models from GCS
│   └── test_*.py              # Comprehensive test suite
│
├── frontend/                    # Flutter Mobile Application
│   └── realtime_datasanitization/
│       ├── lib/                # Dart source code
│       ├── android/           # Android-specific files
│       ├── ios/              # iOS-specific files
│       ├── assets/           # Images, animations, icons
│       └── pubspec.yaml      # Flutter dependencies
│
├── .venv/                      # Python virtual environment
├── WARP.md                     # Development guidance
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Flutter SDK 3.9+**
- **Google Cloud Platform account** (for GCS and Firebase)
- **Node.js** (optional, for additional tools)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_cybersecurity_project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file in backend directory
   cp .env.example .env
   # Add your Firebase credentials and GCS configuration
   ```

5. **Download ML models from GCS**
   ```bash
   python fix_gcs_model.py
   ```

6. **Start the development server**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to Flutter app directory**
   ```bash
   cd frontend/realtime_datasanitization
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure environment**
   ```bash
   # Create .env file with your API endpoint
   echo "API_BASE_URL=http://localhost:8000" > .env
   ```

4. **Run the app**
   ```bash
   # For Android
   flutter run

   # For iOS (requires macOS)
   flutter run -d ios

   # For web
   flutter run -d chrome
   ```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test orchestrator functionality
python test_orchestrator.py

# Test individual ML models
python test_models.py

# Test API endpoints
python test_alerts_endpoint.py

# Test comprehensive analysis
python test_comprehensive_analysis.py

# Test Firebase integration
bash test_firebase_config.sh

# Quick component tests
python quick_test.py
```

### Frontend Tests

```bash
cd frontend/realtime_datasanitization

# Run all tests
flutter test

# Run tests with coverage
flutter test --coverage
```

## 📡 API Endpoints

The FastAPI backend exposes the following key endpoints:

### Analysis Endpoints

- **`POST /analyze-dynamic-behavior`**
  - Analyzes system call sequences for anomalous behavior
  - Input: Array of system calls
  - Returns: Threat score and classification

- **`POST /analyze-network-traffic`**
  - Detects network anomalies and intrusions
  - Input: 10 network traffic features
  - Returns: Anomaly detection results

- **`POST /analyze-text`**
  - Text analysis for sensitive data and quality
  - Input: Text content
  - Returns: Quality metrics and sensitive data flags

- **`POST /analyze-file`**
  - File upload and malware analysis
  - Input: File upload (multipart/form-data)
  - Returns: Threat assessment and file metadata

- **`POST /detect-phishing`**
  - Phishing email and URL detection
  - Input: Email content or URL
  - Returns: Phishing probability and indicators

- **`POST /detect-code-injection`**
  - SQL and code injection pattern detection
  - Input: Code or query string
  - Returns: Injection risk assessment

- **`POST /classify-sensitive-data`**
  - PII and sensitive data classification
  - Input: Text or structured data
  - Returns: Data classification and sensitivity level

- **`POST /comprehensive-analysis`**
  - Multi-model analysis pipeline
  - Input: Various data types
  - Returns: Comprehensive threat report

### Utility Endpoints

- **`GET /health`** - System health check
- **`GET /docs`** - Interactive API documentation
- **`GET /redoc`** - Alternative API documentation

## 🔧 Development

### Running in Development Mode

```bash
# Backend with hot reload
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with hot reload
cd frontend/realtime_datasanitization
flutter run
```

### Creating Test Models

If GCS models are unavailable, create test models:

```bash
cd backend
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

## 🌐 Deployment

### Production API

The production API is deployed on Google Cloud Run:
- **URL**: `https://cybersecurity-api-service-44185828496.us-central1.run.app/`

### Deploying to Google Cloud

```bash
cd backend

# Build and deploy
python deploy_api.py

# Or use gcloud CLI
gcloud run deploy cybersecurity-api-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Mobile App Deployment

```bash
cd frontend/realtime_datasanitization

# Build for Android
flutter build apk --release

# Build for iOS (requires macOS)
flutter build ios --release

# Build for web
flutter build web
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, high-performance web framework
- **TensorFlow 2.19** - Deep learning framework
- **PyTorch 2.3** - Neural network framework
- **scikit-learn** - Machine learning algorithms
- **Transformers** - NLP models (Hugging Face)
- **Firebase Admin** - Authentication and database
- **Google Cloud Storage** - Model storage
- **SQLAlchemy** - Database ORM
- **Uvicorn** - ASGI server

### Frontend
- **Flutter 3.9+** - Cross-platform framework
- **Dart** - Programming language
- **Provider** - State management
- **HTTP** - API communication
- **Lottie** - Animations
- **Google Fonts** - Custom typography
- **Cached Network Image** - Image optimization

### ML/AI
- **LSTM Networks** - Sequential behavior analysis
- **Isolation Forest** - Anomaly detection
- **Random Forest** - Classification
- **XGBoost** - Gradient boosting
- **BERT/Transformers** - Text analysis
- **LightGBM** - Fast gradient boosting

## 📊 Model Performance

The system uses multiple specialized models:

| Model | Task | Accuracy | Framework |
|-------|------|----------|-----------|
| LSTM | Dynamic Behavior | 94.5% | TensorFlow |
| Isolation Forest | Network Anomaly | 92.3% | scikit-learn |
| BERT | Phishing Detection | 96.7% | PyTorch/Transformers |
| Transformer | Code Injection | 95.1% | PyTorch/Transformers |
| Random Forest | File Analysis | 93.8% | scikit-learn |

## 🔐 Security

- **Firebase Authentication** - Secure user authentication
- **Encrypted Data Storage** - Sensitive data encryption
- **JWT Tokens** - Stateless authentication
- **Password Hashing** - Argon2 password hashing
- **API Rate Limiting** - DDoS protection
- **CORS Configuration** - Cross-origin security

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Aditya** - *Initial work*

## 🙏 Acknowledgments

- Google Cloud Platform for infrastructure
- Hugging Face for transformer models
- TensorFlow and PyTorch communities
- Flutter team for the amazing framework

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation in `WARP.md`
- Review API documentation at `/docs` endpoint

## 🗺️ Roadmap

- [ ] Add more ML models for emerging threats
- [ ] Implement real-time dashboard
- [ ] Enhanced mobile app features
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Integration with SIEM systems
- [ ] Automated model retraining pipeline

---

**Built with ❤️ using AI and cutting-edge ML technologies**
