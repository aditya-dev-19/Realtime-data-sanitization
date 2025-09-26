import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/scan_result.dart';

class ThreatProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  // State
  bool _isLoading = false;
  String? _error;
  ScanResult? _lastScanResult;
  final List<ScanResult> _scanHistory = [];
  
  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  ScanResult? get lastScanResult => _lastScanResult;
  List<ScanResult> get scanHistory => List.unmodifiable(_scanHistory);
  int get totalScans => _scanHistory.length;
  String _determineThreatType(Map<String, dynamic> analysis) {
    final results = analysis['results'] ?? {};

    // Check for phishing
    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      return 'Phishing Attempt';
    }

    // Check for code injection
    if ((results['code_injection']?['status'] == 'Injection') || (results['code_injection']?['is_injection'] ?? false) == true) {
      return 'Code Injection Detected';
    }

    // Check for sensitive data
    if ((results['sensitive_data']?['classification'] != null &&
         results['sensitive_data']['classification'] != 'UNKNOWN' &&
         results['sensitive_data']['classification'] != 'ERROR') ||
        (results['sensitive_data']?['has_sensitive_data'] ?? false) == true) {
      return 'Sensitive Data Found';
    }

    // Check for poor data quality
    if ((results['data_quality']?['quality_score'] ?? 1.0) < 0.7) {
      return 'Data Quality Issues';
    }

    return 'No Threats Detected';
  }

  String _generateThreatDetails(Map<String, dynamic> analysis) {
    final results = analysis['results'] ?? {};
    final List<String> threats = [];

    // Phishing details
    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      final phishing = results['phishing'];
      if (phishing?['suspicious_urls'] != null && (phishing['suspicious_urls'] as List).isNotEmpty) {
        threats.add('Suspicious URLs: ${(phishing['suspicious_urls'] as List).length} found');
      }
      if (phishing?['contains_urgency_keywords'] == true) {
        threats.add('Urgency indicators detected');
      }
      if (phishing?['confidence'] != null) {
        threats.add('Phishing confidence: ${(phishing['confidence'] * 100).toStringAsFixed(1)}%');
      }
    }

    // Code injection details
    if ((results['code_injection']?['status'] == 'Injection') || (results['code_injection']?['is_injection'] ?? false) == true) {
      final injection = results['code_injection'];
      if (injection?['detected_patterns'] != null && (injection['detected_patterns'] as List).isNotEmpty) {
        threats.add('Suspicious code patterns: ${(injection['detected_patterns'] as List).length} found');
      }
      if (injection?['confidence'] != null) {
        threats.add('Injection confidence: ${(injection['confidence'] * 100).toStringAsFixed(1)}%');
      }
    }

    // Sensitive data details
    if ((results['sensitive_data']?['classification'] != null &&
         results['sensitive_data']['classification'] != 'UNKNOWN' &&
         results['sensitive_data']['classification'] != 'ERROR') ||
        (results['sensitive_data']?['has_sensitive_data'] ?? false) == true) {
      final sensitive = results['sensitive_data'];
      if (sensitive?['classification'] != null) {
        threats.add('Data classification: ${sensitive['classification']}');
      }
      if (sensitive?['confidence'] != null) {
        threats.add('Classification confidence: ${(sensitive['confidence'] * 100).toStringAsFixed(1)}%');
      }
    }

    // Data quality details
    if ((results['data_quality']?['quality_score'] ?? 1.0) < 0.7) {
      final quality = results['data_quality'];
      if (quality?['quality_score'] != null) {
        threats.add('Quality score: ${(quality['quality_score'] * 100).toStringAsFixed(1)}%');
      }
      if (quality?['issues'] != null && (quality['issues'] as List).isNotEmpty) {
        threats.add('Quality issues: ${(quality['issues'] as List).length} found');
      }
    }

    return threats.isEmpty ? 'No specific threats detected' : threats.join(' • ');
  }

  List<String> _generateRecommendedActions(Map<String, dynamic> analysis) {
    final results = analysis['results'] ?? {};
    final List<String> actions = [];

    // Phishing recommendations
    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      actions.add('Do not click on any links in this content');
      actions.add('Verify the sender before taking any action');
      actions.add('Delete this message immediately');
    }

    // Code injection recommendations
    if ((results['code_injection']?['status'] == 'Injection') || (results['code_injection']?['is_injection'] ?? false) == true) {
      actions.add('Do not execute this code');
      actions.add('Review the input for suspicious patterns');
      actions.add('Use parameterized queries for database interactions');
    }

    // Sensitive data recommendations
    if ((results['sensitive_data']?['classification'] != null &&
         results['sensitive_data']['classification'] != 'UNKNOWN' &&
         results['sensitive_data']['classification'] != 'ERROR') ||
        (results['sensitive_data']?['has_sensitive_data'] ?? false) == true) {
      actions.add('Remove or redact sensitive information before sharing');
      actions.add('Review data handling policies');
      actions.add('Consider encrypting this data if it needs to be stored');
    }

    // Data quality recommendations
    if ((results['data_quality']?['quality_score'] ?? 1.0) < 0.7) {
      actions.add('Review the data ingestion pipeline');
      actions.add('Ensure data is complete, consistent, and properly formatted');
      actions.add('Check data sources for quality issues');
    }

    return actions.isNotEmpty ? actions : ['No specific actions required'];
  }

  Future<ScanResult?> analyzeText(String text) async {
  if (text.trim().isEmpty) {
    _error = 'Please enter some text to analyze';
    notifyListeners();
    return null;
  }
  
  _isLoading = true;
  _error = null;
  notifyListeners();

  try {
    final apiService = ApiService();
    final analysis = await apiService.runComprehensiveAnalysis(text);
    
    final result = ScanResult(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      isThreat: analysis['overall_risk_score'] > 0.5, // Adjust threshold as needed
      threatType: _determineThreatType(analysis),
      threatDetails: _generateThreatDetails(analysis),
      threatScore: analysis['overall_risk_score'],
      scannedContentPreview: text.length > 100 ? '${text.substring(0, 100)}...' : text,
      scanType: 'comprehensive',
      recommendedActions: _generateRecommendedActions(analysis),
      rawAnalysis: analysis,
    );
    
    _lastScanResult = result;
    _scanHistory.insert(0, result);
    return result;
    
  } catch (e) {
    _error = 'Failed to analyze text: $e';
    debugPrint('Analysis error: $_error');
    return null;
  } finally {
    _isLoading = false;
    notifyListeners();
  }
}

  /// Analyze a file for potential threats using comprehensive analysis
  Future<ScanResult?> analyzeFile(PlatformFile file) async {
    if ((file.bytes == null || file.bytes!.isEmpty) && (file.path == null || file.path!.isEmpty)) {
      _error = 'Selected file is empty or invalid';
      notifyListeners();
      return null;
    }
    
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final apiService = ApiService();
      final analysis = await apiService.analyzeFileComprehensive(file);
      
      final result = ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        isThreat: analysis['overall_risk_score'] > 0.5, // Adjust threshold as needed
        threatType: _determineThreatType(analysis),
        threatDetails: _generateThreatDetails(analysis),
        threatScore: analysis['overall_risk_score'],
        scannedContentPreview: 'File: ${file.name} (${_formatFileSize(file.size)})',
        scanType: 'comprehensive_file',
        recommendedActions: _generateRecommendedActions(analysis),
        rawAnalysis: analysis,
        metadata: {
          'filename': file.name,
          'file_size': file.size,
          'file_type': file.extension,
        },
      );
      
      _lastScanResult = result;
      _scanHistory.insert(0, result);
      return result;
      
    } catch (e) {
      _error = 'Failed to analyze file: ${e.toString()}';
      debugPrint('File analysis error: $_error');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Clear the scan history
  void clearHistory() {
    _scanHistory.clear();
    _lastScanResult = null;
    notifyListeners();
  }
  
  // Helper method to format file size
  String _formatFileSize(int? bytes) {
    if (bytes == null) return '0 B';
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
  
  // Simulate threat detection logic (for demo purposes)
  bool _simulateThreatDetection(String text) {
    final lowerText = text.toLowerCase();
    final suspiciousPatterns = [
      'password',
      'credit card',
      'social security',
      'ssn',
      'account number',
      'bank account',
      'malware',
      'virus',
      'hack',
      'exploit',
    ];
    
    return suspiciousPatterns.any((pattern) => lowerText.contains(pattern));
  }
}