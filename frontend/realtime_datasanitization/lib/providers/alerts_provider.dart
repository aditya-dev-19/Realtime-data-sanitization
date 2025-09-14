import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/alert.dart';

class AlertsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  List<Alert> _alerts = [];
  String _error = '';

  bool get isLoading => _isLoading;
  List<Alert> get alerts => _alerts;
  String get error => _error;

  // Get unread alerts count
  int get unreadCount => _alerts.where((alert) => !alert.read).length;

  // Get alerts by severity
  List<Alert> get highPriorityAlerts =>
      _alerts.where((alert) => alert.severity == 'high').toList();
  List<Alert> get mediumPriorityAlerts =>
      _alerts.where((alert) => alert.severity == 'medium').toList();
  List<Alert> get lowPriorityAlerts =>
      _alerts.where((alert) => alert.severity == 'low').toList();

  // Fetch alerts from the API
  Future<void> fetchAlerts() async {
    if (_isLoading) return;
    
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      final alertsData = await _apiService.getAlerts();
      _alerts = alertsData
          .map((alert) => Alert.fromJson(alert as Map<String, dynamic>))
          .toList();
    } catch (e) {
      _error = 'Failed to load alerts: ${e.toString()}';
      if (kDebugMode) {
        print('Alerts error: $_error');
      }
      // Fallback to mock data if API fails (for development)
      _alerts = [
        Alert(
          id: '1',
          title: 'Suspicious Activity Detected',
          message: 'Multiple failed login attempts detected from a new device.',
          timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
          severity: 'high',
        ),
        Alert(
          id: '2',
          title: 'System Update Available',
          message: 'A new security update is available for your system.',
          timestamp: DateTime.now().subtract(const Duration(hours: 2)),
          severity: 'medium',
        ),
        Alert(
          id: '3',
          title: 'New Security Policy',
          message: 'Please review and accept the updated security policy.',
          timestamp: DateTime.now().subtract(const Duration(days: 1)),
          severity: 'low',
          read: true,
        ),
      ];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Mark an alert as read
  Future<void> markAsRead(String alertId) async {
    final index = _alerts.indexWhere((alert) => alert.id == alertId);
    if (index == -1) return;
    
    if (!_alerts[index].read) {
      _alerts[index] = _alerts[index].copyWith(read: true);
      notifyListeners();
      
      // Update on the server
      try {
        await _apiService.markAlertAsRead(alertId);
      } catch (e) {
        // Revert if the API call fails
        _alerts[index] = _alerts[index].copyWith(read: false);
        notifyListeners();
        rethrow;
      }
    }
  }
  
  // Mark all alerts as read
  Future<void> markAllAsRead() async {
    bool hasUnread = _alerts.any((alert) => !alert.read);
    if (!hasUnread) return;
    
    // Update local state optimistically
    _alerts = _alerts.map((alert) => alert.copyWith(read: true)).toList();
    notifyListeners();
    
    // Update on the server
    try {
      // This is a simplified implementation - in a real app, you'd need an endpoint
      // to mark all alerts as read at once
      for (final alert in _alerts) {
        if (!alert.read) {
          await _apiService.markAlertAsRead(alert.id);
        }
      }
    } catch (e) {
      // Revert if the API call fails
      _alerts = _alerts.map((alert) => alert.copyWith(read: false)).toList();
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
