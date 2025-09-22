import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import '../models/alert.dart';

class ApiService {
  // Base URL for the API with version prefix
  static const String _baseUrl = 'https://cybersecurity-api-service-44185828496.us-central1.run.app';
  
  // Headers for API requests
  final Map<String, String> _headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  // Add authentication token to headers if available
  String? _authToken;
  
  // Set authentication token
  void setAuthToken(String token) {
    _authToken = token;
    _headers['Authorization'] = 'Bearer $token';
  }
  
  // Clear authentication token
  void clearAuthToken() {
    _authToken = null;
    _headers.remove('Authorization');
  }

  // Auth
  Future<Map<String, dynamic>> login(String email, String password) async {
  try {
    final url = '${_baseUrl}/token'; // Note: no leading slash
    debugPrint('Attempting login to: $url');
    
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    debugPrint('Login response status: ${response.statusCode}');
    debugPrint('Response body: ${response.body}');

    if (response.statusCode == 200) {
      final responseData = jsonDecode(utf8.decode(response.bodyBytes));
      if (responseData is! Map<String, dynamic>) {
        throw Exception('Invalid response format from server');
      }
      if (responseData['access_token'] == null) {
        throw Exception('No access token in response');
      }
      return responseData;
    } else {
      final error = jsonDecode(response.body);
      final errorMessage = error['detail'] ?? 'Login failed';
      throw Exception(errorMessage);
    }
  } catch (e) {
    debugPrint('Error in login: $e');
    rethrow;
  }
}

Future<void> register(String email, String password) async {
  try {
    final url = '${_baseUrl}/register'; // Note: no leading slash
    debugPrint('Attempting registration at: $url');
    
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    debugPrint('Register response status: ${response.statusCode}');
    debugPrint('Response body: ${response.body}');

    if (response.statusCode != 200 && response.statusCode != 201) {
      final error = jsonDecode(response.body);
      final errorMessage = error['detail'] ?? 'Registration failed';
      throw Exception(errorMessage);
    }
  } catch (e) {
    debugPrint('Error in register: $e');
    rethrow;
  }
}

// Phishing detection
Future<Map<String, dynamic>> detectPhishing(String text) async {
  return _makeApiRequest('/detect-phishing', {'text': text});
}

// Code injection detection
Future<Map<String, dynamic>> detectCodeInjection(String text) async {
  return _makeApiRequest('/detect-code-injection', {'text': text});
}

// Comprehensive analysis
Future<Map<String, dynamic>> runComprehensiveAnalysis(String text) async {
  return _makeApiRequest('/comprehensive-analysis', {'text': text});
}

// Helper method for API requests
Future<Map<String, dynamic>> _makeApiRequest(
  String endpoint, 
  Map<String, dynamic> data
) async {
  try {
    final response = await http.post(
      Uri.parse('$_baseUrl$endpoint'),
      headers: _headers,
      body: jsonEncode(data),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception('API request failed: ${response.statusCode}');
    }
  } catch (e) {
    debugPrint('API Error: $e');
    rethrow;
  }
}
  // Alerts
  Future<List<dynamic>> getAlerts({int limit = 100, String? status, String? severity, int offset = 0}) async {
    try {
      // Build query parameters
      final params = {
        'limit': limit.toString(),
        'offset': offset.toString(),
        if (status != null) 'status': status,
        if (severity != null) 'severity': severity,
      };
      
      final uri = Uri.parse('$_baseUrl/alerts').replace(queryParameters: params);
      final response = await http.get(uri, headers: _headers);
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes)) as List;
      } else {
        throw Exception('Failed to load alerts: ${response.statusCode}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching alerts: $e');
      }
      rethrow;
    }
  }

  // Update alert status
  Future<void> updateAlertStatus(int alertId, AlertStatus status) async {
    try {
      final response = await http.put(
        Uri.parse('$_baseUrl/alerts/$alertId/status'),
        headers: _headers,
        body: jsonEncode({'status': status.toString().split('.').last}),
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to update alert status: ${response.statusCode}');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error updating alert status: $e');
      }
      rethrow;
    }
  }
  
  // Mark alert as read
  Future<bool> markAlertAsRead(String alertId) async {
    try {
      await updateAlertStatus(int.parse(alertId), AlertStatus.resolved);
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('Error marking alert as read: $e');
      }
      return false;
    }
  }

  // Mark all alerts as read
  Future<bool> markAllAlertsAsRead() async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/alerts/mark-all-read'),
        headers: _headers,
      );
      
      return response.statusCode == 200;
    } catch (e) {
      if (kDebugMode) {
        print('Error marking all alerts as read: $e');
      }
      return false;
    }
  }

  // System Health
  Future<Map<String, dynamic>> getSystemHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        
        // Map the API response to our expected format
        return {
          'status': data['status']?.toLowerCase() ?? 'unknown',
          'details': data['message'] ?? 'System status unknown',
          'timestamp': DateTime.now().toIso8601String(),
          'components': <String, dynamic>{
            'orchestrator': data['components']?['orchestrator_status']?.toString() ?? 'unknown',
            'database': (data['components']?['database']?.toString().contains('error') ?? false) 
                ? 'error' 
                : 'ok',
            'network_traffic': 'ok', // Default value since not in response
            'data_classification': 'ok', // Default value since not in response
            'enhanced_features': false, // Default value
          },
          'totalScans': 0, // These will be updated when we have the actual endpoints
          'threatsDetected': 0,
          'recentScans': [],
          'threatStats': {
            'totalThreats': 0,
            'threatsByType': {},
          },
        };
      } else {
        throw Exception('Failed to fetch system health: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getSystemHealth: $e');
      // Return a default health status on error
      return {
        'status': 'error',
        'details': 'Error checking system health: $e',
        'timestamp': DateTime.now().toIso8601String(),
        'components': {
          'orchestrator': 'UNKNOWN',
          'dynamic_behavior': 'UNKNOWN',
          'network_traffic': 'UNKNOWN',
          'data_classification': 'BASIC',
          'enhanced_features': false,
        },
        'totalScans': 0,
        'threatsDetected': 0,
        'recentScans': [],
        'threatStats': {
          'totalThreats': 0,
          'threatsByType': {},
        },
      };
    }
  }
  
  
  // Get Dashboard Data - Mock implementation since there's no dedicated endpoint
  Future<Map<String, dynamic>> getDashboardData() async {
    try {
      // Get system health as part of dashboard data
      final healthStatus = await getSystemHealth();
      
      // Return mock data with health status
      return {
        'totalScans': 0,
        'threatsDetected': 0,
        'filesScanned': 0,
        'avgScanTime': 0,
        'systemStatus': healthStatus['status'] ?? 'unknown',
        'lastChecked': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('Error in getDashboardData: $e');
      // Return minimal data on error
      return {
        'totalScans': 0,
        'threatsDetected': 0,
        'filesScanned': 0,
        'avgScanTime': 0,
        'systemStatus': 'error',
        'error': e.toString(),
      };
    }
  }
  
  // Analyze Text for Threats
  Future<Map<String, dynamic>> analyzeText(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/analyze-text'),
        headers: _headers,
        body: jsonEncode({'text': text}),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to analyze text: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in analyzeText: $e');
      rethrow;
    }
  }
  
  // Analyze File for Threats
  Future<Map<String, dynamic>> analyzeFile(PlatformFile file) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl/analyze-file'),
      );
      
      // Add headers
      _headers.forEach((key, value) {
        if (key.toLowerCase() != 'content-type') { // Don't set Content-Type for multipart
          request.headers[key] = value;
        }
      });
      
      // Add file
      if (file.bytes != null) {
        request.files.add(http.MultipartFile.fromBytes(
          'file',
          file.bytes!,
          filename: file.name,
        ));
      } else if (file.path != null) {
        request.files.add(await http.MultipartFile.fromPath(
          'file',
          file.path!,
          filename: file.name,
        ));
      } else {
        throw Exception('No file data available');
      }
      
      // Send request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to analyze file: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in analyzeFile: $e');
      rethrow;
    }
  }
  
  // Get Scan History - Not implemented in backend, return empty list
  Future<List<dynamic>> getScanHistory({int limit = 10, int offset = 0}) async {
    try {
      debugPrint('Scan history endpoint not implemented, returning empty list');
      return [];
    } catch (e) {
      debugPrint('Error in getScanHistory: $e');
      return [];
    }
  }
  
  // Get Scan Result - Not implemented in backend, return empty result
  Future<Map<String, dynamic>> getScanResult(String scanId) async {
    try {
      debugPrint('Get scan result endpoint not implemented, returning empty result');
      return {
        'id': scanId,
        'status': 'completed',
        'result': {
          'is_malicious': false,
          'threats_found': [],
          'confidence': 0.0,
        },
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('Error in getScanResult: $e');
      return {
        'id': scanId,
        'status': 'error',
        'error': e.toString(),
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  }
  
  // Get System Stats
  Future<Map<String, dynamic>> getSystemStats() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/model-stats'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        // Return default stats if the endpoint fails
        return {
          'model_stats': {
            'sensitive_data_model': 'operational',
            'quality_assessment_model': 'operational',
            'last_updated': DateTime.now().toIso8601String(),
          },
          'system_status': 'operational',
          'timestamp': DateTime.now().toIso8601String(),
        };
      }
    } catch (e) {
      debugPrint('Error in getSystemStats: $e');
      return {
        'error': 'Failed to get system stats: $e',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  }
}
