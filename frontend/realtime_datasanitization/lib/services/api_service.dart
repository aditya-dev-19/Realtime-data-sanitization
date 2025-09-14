import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';

class ApiService {
  // Base URL for the API
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

  // System Health
  Future<Map<String, dynamic>> getSystemHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/health'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to get system health: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getSystemHealth: $e');
      rethrow;
    }
  }
  
  // Get Alerts
  Future<List<dynamic>> getAlerts({int limit = 20, int offset = 0}) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/alerts?limit=$limit&offset=$offset'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return data is List ? data : [];
      } else {
        throw Exception('Failed to load alerts: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getAlerts: $e');
      rethrow;
    }
  }
  
  // Mark Alert as Read
  Future<bool> markAlertAsRead(String alertId) async {
    try {
      final response = await http.patch(
        Uri.parse('$_baseUrl/api/alerts/$alertId/read'),
        headers: _headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error in markAlertAsRead: $e');
      return false;
    }
  }
  
  // Mark All Alerts as Read
  Future<bool> markAllAlertsAsRead() async {
    try {
      final response = await http.patch(
        Uri.parse('$_baseUrl/api/alerts/read-all'),
        headers: _headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error in markAllAlertsAsRead: $e');
      return false;
    }
  }
  
  // Get Dashboard Data
  Future<Map<String, dynamic>> getDashboardData() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/dashboard'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to load dashboard data: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getDashboardData: $e');
      rethrow;
    }
  }
  
  // Analyze Text for Threats
  Future<Map<String, dynamic>> analyzeText(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/analyze/text'),
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
        Uri.parse('$_baseUrl/api/analyze/file'),
      );
      
      // Add headers
      _headers.forEach((key, value) {
        request.headers[key] = value;
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
  
  // Get Scan History
  Future<List<dynamic>> getScanHistory({int limit = 10, int offset = 0}) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/scans?limit=$limit&offset=$offset'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return data is List ? data : [];
      } else {
        throw Exception('Failed to load scan history: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getScanHistory: $e');
      rethrow;
    }
  }
  
  // Get Scan Result
  Future<Map<String, dynamic>> getScanResult(String scanId) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/scans/$scanId'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to load scan result: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getScanResult: $e');
      rethrow;
    }
  }
  
  // Get System Statistics
  Future<Map<String, dynamic>> getSystemStats() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/stats'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Failed to load system stats: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('Error in getSystemStats: $e');
      rethrow;
    }
  }
}
