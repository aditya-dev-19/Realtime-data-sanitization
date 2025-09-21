import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/alert.dart';

class AlertsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  List<Alert> _alerts = [];
  String _error = '';
  DateTime? _lastFetched;

  bool get isLoading => _isLoading;
  List<Alert> get alerts => List.unmodifiable(_alerts);
  String get error => _error;
  bool get hasError => _error.isNotEmpty;
  DateTime? get lastFetched => _lastFetched;

  // Get unread alerts count
  int get unreadCount => _alerts.where((alert) => !alert.isRead).length;

  // Get alerts by status
  List<Alert> get openAlerts => _alerts
      .where((alert) => alert.status == AlertStatus.open)
      .toList();
  List<Alert> get inProgressAlerts => _alerts
      .where((alert) => alert.status == AlertStatus.in_progress)
      .toList();
  List<Alert> get resolvedAlerts => _alerts
      .where((alert) => alert.status == AlertStatus.resolved)
      .toList();
  List<Alert> get dismissedAlerts => _alerts
      .where((alert) => alert.status == AlertStatus.dismissed)
      .toList();

  // Get alerts by severity
  List<Alert> getCriticalAlerts() => _getAlertsBySeverity(AlertSeverity.critical);
  List<Alert> getHighPriorityAlerts() => _getAlertsBySeverity(AlertSeverity.high);
  List<Alert> getMediumPriorityAlerts() => _getAlertsBySeverity(AlertSeverity.medium);
  List<Alert> getLowPriorityAlerts() => _getAlertsBySeverity(AlertSeverity.low);

  // Get alerts by type
  List<Alert> getThreatAlerts() => _getAlertsByType(AlertType.threat_detected);
  List<Alert> getSystemIssues() => _getAlertsByType(AlertType.system_issue);
  List<Alert> getSecurityAlerts() => _getAlertsByType(AlertType.security_alert);
  List<Alert> getPerformanceIssues() => _getAlertsByType(AlertType.performance_issue);
  List<Alert> getConfigChanges() => _getAlertsByType(AlertType.configuration_change);

  // Helper methods for filtering
  List<Alert> _getAlertsBySeverity(AlertSeverity severity) {
    return _alerts.where((alert) => alert.severity == severity).toList();
  }

  List<Alert> _getAlertsByType(AlertType type) {
    return _alerts.where((alert) => alert.type == type).toList();
  }

  // Fetch alerts from the API
  Future<void> fetchAlerts({bool forceRefresh = false}) async {
    // Don't refresh if already loading or recently fetched (unless forced)
    if (_isLoading || (!forceRefresh && _lastFetched != null && 
        DateTime.now().difference(_lastFetched!) < const Duration(minutes: 1))) {
      return;
    }
    
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      final alertsData = await _apiService.getAlerts();
      _alerts = alertsData
          .map<Alert>((alert) => Alert.fromJson(alert as Map<String, dynamic>))
          .toList();
      _lastFetched = DateTime.now();
    } catch (e) {
      _error = 'Failed to load alerts: ${e.toString()}';
      if (kDebugMode) {
        print('Alerts error: $_error');
      }
      // Don't clear existing alerts on error to prevent UI flicker
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Get a specific alert by ID
  Alert? getAlertById(String id) {
    try {
      return _alerts.firstWhere((alert) => alert.id == id);
    } catch (e) {
      return null;
    }
  }
  
  // Update alert status
  Future<void> updateAlertStatus(String alertId, AlertStatus newStatus) async {
    final index = _alerts.indexWhere((alert) => alert.id == alertId);
    if (index == -1) return;
    
    final currentAlert = _alerts[index];
    if (currentAlert.status == newStatus) return;
    
    // Optimistic update
    final updatedAlert = currentAlert.copyWith(
      status: newStatus,
      resolvedAt: newStatus == AlertStatus.resolved ? DateTime.now() : null,
    );
    
    _alerts[index] = updatedAlert;
    notifyListeners();
    
    // Update on the server
    try {
      await _apiService.updateAlertStatus(int.parse(alertId), newStatus);
    } catch (e) {
      // Revert if the API call fails
      _alerts[index] = currentAlert;
      notifyListeners();
      rethrow;
    }
  }
  
  // Mark an alert as read (alias for updating status to resolved)
  Future<void> markAsRead(String alertId) async {
    await updateAlertStatus(alertId, AlertStatus.resolved);
  }
  
  // Mark all alerts as read
  Future<void> markAllAsRead() async {
    if (_alerts.every((alert) => alert.isRead)) return;
    
    // Optimistic update
    final List<Alert> updatedAlerts = _alerts.map((alert) {
      return alert.isRead 
          ? alert 
          : alert.copyWith(
              status: AlertStatus.resolved,
              resolvedAt: DateTime.now(),
            );
    }).toList();
    
    final List<Alert> previousAlerts = List.from(_alerts);
    _alerts = updatedAlerts;
    notifyListeners();
    
    // Update on the server
    try {
      await _apiService.markAllAlertsAsRead();
    } catch (e) {
      // Revert if the API call fails
      _alerts = previousAlerts;
      notifyListeners();
      rethrow;
    }
  }
  
  // Clear all alerts
  void clearAll() {
    _alerts = [];
    notifyListeners();
  }
}
