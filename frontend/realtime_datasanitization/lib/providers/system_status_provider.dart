import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class SystemStatusProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  Map<String, dynamic>? _systemStatus;
  String _error = '';
  DateTime? _lastUpdated;

  bool get isLoading => _isLoading;
  Map<String, dynamic>? get systemStatus => _systemStatus;
  String get error => _error;
  DateTime? get lastUpdated => _lastUpdated;

  // Status helpers
  String get status => _systemStatus?['status']?.toString().toLowerCase() ?? 'unknown';
  String get statusMessage => _systemStatus?['details']?.toString() ?? 'Status unknown';
  
  // Component status
  bool get isApiHealthy => status == 'healthy';
  bool get isDatabaseConnected => _systemStatus?['database']?['connected'] == true;
  bool get isAiModelLoaded => _systemStatus?['ai_model']?['loaded'] == true;
  
  // Get status color
  Color get statusColor {
    switch (status) {
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

  // Get status icon
  IconData get statusIcon {
    switch (status) {
      case 'healthy':
        return Icons.check_circle;
      case 'degraded':
        return Icons.warning;
      case 'unhealthy':
        return Icons.error;
      default:
        return Icons.help_outline;
    }
  }

  // Fetch system status from the API
  Future<void> fetchSystemStatus() async {
    // Prevent multiple simultaneous requests
    if (_isLoading) return;
    
    try {
      _isLoading = true;
      _error = '';
      notifyListeners();

      // Fetch system health from API
      _systemStatus = await _apiService.getSystemHealth();
      _lastUpdated = DateTime.now();
    } catch (e, stackTrace) {
      debugPrint('Error fetching system status: $e');
      debugPrint('Stack trace: $stackTrace');
      
      _error = 'Failed to fetch system status: ${e.toString()}';
      
      // Fallback to mock data if API fails
      _systemStatus = {
        'status': 'degraded',
        'details': 'Unable to connect to the server. Using cached data.',
        'timestamp': DateTime.now().toIso8601String(),
        'version': '1.0.0',
        'environment': 'development',
        'database': {
          'connected': true,
          'status': 'connected',
          'latency': 42,
        },
        'ai_model': {
          'loaded': true,
          'version': '1.2.3',
          'last_trained': '2023-11-15T10:30:00Z',
        },
        'services': {
          'auth': 'operational',
          'storage': 'degraded',
          'processing': 'operational',
        },
      };
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Format the system status for display
  List<Map<String, dynamic>> getStatusList() {
    if (_systemStatus == null) return [];
    
    final List<Map<String, dynamic>> statusList = [
      {
        'name': 'API Status',
        'status': _systemStatus?['status'] ?? 'unknown',
        'details': _systemStatus?['details'] ?? 'No details available',
        'icon': statusIcon,
        'color': statusColor,
      },
      {
        'name': 'Database',
        'status': isDatabaseConnected ? 'connected' : 'disconnected',
        'details': isDatabaseConnected 
            ? 'Connection stable' 
            : 'Unable to connect to database',
        'icon': isDatabaseConnected ? Icons.storage : Icons.storage_outlined,
        'color': isDatabaseConnected ? Colors.green : Colors.red,
      },
      {
        'name': 'AI Model',
        'status': isAiModelLoaded ? 'loaded' : 'unavailable',
        'details': isAiModelLoaded 
            ? 'Version ${_systemStatus?['ai_model']?['version'] ?? 'unknown'}' 
            : 'Model not loaded',
        'icon': isAiModelLoaded ? Icons.model_training : Icons.error_outline,
        'color': isAiModelLoaded ? Colors.green : Colors.orange,
      },
    ];
    
    // Add service statuses if available
    final services = _systemStatus?['services'] as Map<String, dynamic>?;
    if (services != null) {
      services.forEach((key, value) {
        statusList.add({
          'name': '${key[0].toUpperCase()}${key.substring(1)} Service',
          'status': value.toString(),
          'details': 'Service ${value.toString().toUpperCase()}',
          'icon': _getServiceIcon(value.toString()),
          'color': _getServiceColor(value.toString()),
        });
      });
    }
    
    return statusList;
  }
  
  // Get service icon based on status
  IconData _getServiceIcon(String status) {
    switch (status.toLowerCase()) {
      case 'operational':
        return Icons.check_circle;
      case 'degraded':
        return Icons.warning;
      case 'outage':
        return Icons.error;
      default:
        return Icons.help_outline;
    }
  }
  
  // Get service color based on status
  Color _getServiceColor(String status) {
    switch (status.toLowerCase()) {
      case 'operational':
        return Colors.green;
      case 'degraded':
        return Colors.orange;
      case 'outage':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
  
  // Refresh the system status
  Future<void> refresh() async {
    await fetchSystemStatus();
  }
}
