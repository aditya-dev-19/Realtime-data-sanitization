# Alerts System

This document describes the alerts system implementation for the cybersecurity application.

## Backend Implementation

The alerts system consists of the following components:

### Database Models
- `Alert` model in `api/models/alert.py`
- Database migrations are handled by SQLAlchemy

### API Endpoints
- `GET /alerts/` - List all alerts with optional filtering
- `GET /alerts/{alert_id}` - Get a specific alert by ID
- `PUT /alerts/{alert_id}/status` - Update an alert's status
- `POST /alerts/test/generate` - Generate test alerts (for development)

### Configuration
Update the database connection in `api/database.py` if needed.

## Frontend Implementation

The frontend includes:
- `Alert` model in `lib/models/alert.dart`
- `AlertsProvider` in `lib/providers/alerts_provider.dart` for state management
- API client methods in `lib/services/api_service.dart`

## Setup Instructions

1. **Backend Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Initialize the database
   python init_db.py
   
   # Run the FastAPI server
   uvicorn api.main:app --reload
   ```

2. **Test the Alerts API**
   ```bash
   python test_alerts.py
   ```

3. **Frontend Setup**
   - Make sure the `_baseUrl` in `lib/services/api_service.dart` points to your backend
   - The alerts will be automatically loaded when the app starts

## Alert Types and Severity

### Alert Types
- `threat_detected`: Security threats detected
- `system_issue`: System-related issues
- `security_alert`: General security alerts
- `performance_issue`: Performance-related issues
- `configuration_change`: Configuration changes

### Severity Levels
- `critical`: Requires immediate attention
- `high`: High priority issue
- `medium`: Medium priority issue
- `low`: Low priority issue

## Testing

Use the test script to verify the alerts functionality:

```bash
python test_alerts.py
```

This will:
1. Create test alerts
2. List all alerts
3. Get a specific alert
4. Update an alert's status

## Integration with Other Components

The alerts system is integrated with:
- Authentication system (future)
- Logging system
- Notification system (future)

## Future Enhancements

- Add user-specific alerts
- Implement real-time updates with WebSockets
- Add alert filtering and search
- Support for alert acknowledgments
- Email/SMS notifications for critical alerts
