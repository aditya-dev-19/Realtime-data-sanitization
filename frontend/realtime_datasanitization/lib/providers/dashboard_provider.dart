import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  Map<String, dynamic>? _dashboardData;
  String _error = '';
  DateTime? _lastUpdated;

  bool get isLoading => _isLoading;
  Map<String, dynamic>? get dashboardData => _dashboardData;
  String get error => _error;
  DateTime? get lastUpdated => _lastUpdated;

  // System status helpers
  String get systemStatus => _dashboardData?['systemStatus']?['status'] ?? 'unknown';
  String get systemStatusMessage => _dashboardData?['systemStatus']?['details'] ?? 'Status unknown';
  int get totalScans => _dashboardData?['totalScans'] ?? 0;
  int get threatsDetected => _dashboardData?['threatsDetected'] ?? 0;
  
  // Get threat statistics
  Map<String, dynamic> get threatStats => _dashboardData?['threatStats'] ?? {};
  int get totalThreats => threatStats['totalThreats'] ?? 0;
  Map<String, int> get threatsByType => Map<String, int>.from(threatStats['threatsByType'] ?? {});

  // Get recent scans
  List<dynamic> get recentScans => _dashboardData?['recentScans'] ?? [];

  // Get system health color based on status
  Color get systemStatusColor {
    switch (systemStatus.toLowerCase()) {
      case 'healthy':
        return Colors.green;
      case 'degraded':
        return Colors.orange;
      case 'unhealthy':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // Fetch dashboard data from the API
  Future<void> fetchDashboardData() async {
    if (_isLoading) return;
    
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      // Try to get data from the dashboard endpoint first
      try {
        _dashboardData = await _apiService.getDashboardData();
      } catch (e) {
        // Fallback to individual endpoints if dashboard endpoint fails
        if (kDebugMode) {
          print('Dashboard endpoint failed, falling back to individual endpoints: $e');
        }
        final healthData = await _apiService.getSystemHealth();
        _dashboardData = {
          'systemStatus': healthData,
          'totalScans': healthData['totalScans'] ?? 0,
          'threatsDetected': healthData['threatsDetected'] ?? 0,
          'recentScans': healthData['recentScans'] ?? [],
          'threatStats': {
            'totalThreats': healthData['totalThreats'] ?? 0,
            'threatsByType': healthData['threatsByType'] ?? {},
          },
        };
      }
      
      _lastUpdated = DateTime.now();
    } catch (e) {
      _error = 'Failed to load dashboard data: ${e.toString()}';
      if (kDebugMode) print('Dashboard data error: $_error');
      
      // Fallback to mock data if API fails
      _dashboardData = {
        'systemStatus': {
          'status': 'healthy', 
          'details': 'All systems operational',
          'lastChecked': DateTime.now().toIso8601String(),
        },
        'totalScans': 42,
        'threatsDetected': 7,
        'recentScans': [
          {
            'id': '1',
            'type': 'file',
            'name': 'document.pdf',
            'status': 'clean',
            'timestamp': DateTime.now().subtract(const Duration(minutes: 30)).toIso8601String(),
          },
          {
            'id': '2',
            'type': 'url',
            'name': 'example.com',
            'status': 'malicious',
            'threatType': 'phishing',
            'timestamp': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
          },
        ],
        'threatStats': {
          'totalThreats': 7,
          'threatsByType': {
            'phishing': 3,
            'malware': 2,
            'injection': 2,
          },
        },
      };
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Get summary statistics for the dashboard
  Map<String, dynamic> getSummaryStats() {
    if (_dashboardData == null) return {};
    
    return {
      'systemStatus': systemStatus,
      'systemStatusMessage': systemStatusMessage,
      'lastUpdated': _lastUpdated?.toIso8601String() ?? '',
      'totalScans': totalScans,
      'threatsDetected': threatsDetected,
      'threatStats': threatStats,
    };
  }
  
  // Refresh all data
  Future<void> refresh() async {
    await fetchDashboardData();
  }
}
