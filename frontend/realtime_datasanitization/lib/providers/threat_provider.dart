import 'dart:convert';
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
  List<ScanResult> get scanHistory => List.unmodifiable(_scanHistory);
  int get totalScans => _scanHistory.length;

  bool _determineIsThreat(Map<String, dynamic> analysis) {
    final results = analysis['results'] ?? {};

    print('🔍 DEBUG: Determining threat status');
    print('Phishing: ${results['phishing']}');
    print('Code injection: ${results['code_injection']}');
    print('Sensitive data: ${results['sensitive_data']}');
    print('Data quality: ${results['data_quality']}');

    // Check for phishing
    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      print('🚨 DEBUG: Phishing threat detected');
      return true;
    }

    // Check for code injection
    final codeInjection = results['code_injection'];
    print('💉 DEBUG: Code injection result: $codeInjection');

    if (codeInjection != null) {
      final status = codeInjection['status'];
      final confidence = codeInjection['confidence'];
      print('💉 DEBUG: Code injection - status: $status, confidence: $confidence');

      if (status == 'Injection' || status == 'XSS' || (codeInjection['is_injection'] ?? false) == true) {
        print('💉 DEBUG: Code injection threat detected');
        return true;
      }
    } else {
      print('💉 DEBUG: Code injection result is null');
    }

    // Check for sensitive data
    final sensitiveData = results['sensitive_data'];
    final classification = sensitiveData?['classification'];
    print('🔒 DEBUG: Sensitive data check - classification: $classification, has_sensitive_data: ${sensitiveData?['has_sensitive_data'] ?? false}');

    if (classification != null &&
        classification != 'Safe' &&
        classification != 'UNKNOWN' &&
        classification != 'ERROR' &&
        classification != 'NOT_SENSITIVE') {
      print('🔒 DEBUG: Sensitive data threat detected via classification: $classification');
      return true;
    }

    if ((sensitiveData?['has_sensitive_data'] ?? false) == true) {
      print('🔒 DEBUG: Sensitive data threat detected via has_sensitive_data flag');
      return true;
    }

    final qualityScore = results['data_quality']?['quality_score'] ?? 1.0;
    print('📊 DEBUG: Data quality score: $qualityScore');

    if (qualityScore < 0.7) {
      print('📊 DEBUG: Data quality threat detected');
      return true;
    }

    print('✅ DEBUG: No threats detected');
    return false;
  }

  String _determineThreatType(Map<String, dynamic> analysis) {
    final results = analysis['results'] ?? {};

    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      return 'Phishing Attempt';
    }

    final codeInjection = results['code_injection'];
    if (codeInjection != null && (codeInjection['status'] == 'Injection' || codeInjection['status'] == 'XSS' || (codeInjection['is_injection'] ?? false) == true)) {
      return 'Code Injection Detected';
    }

    final sensitiveData = results['sensitive_data'];
    final classification = sensitiveData?['classification'];
    if (classification != null &&
        classification != 'Safe' &&
        classification != 'UNKNOWN' &&
        classification != 'ERROR' &&
        classification != 'NOT_SENSITIVE') {
      return 'Sensitive Data Found';
    }
    if ((sensitiveData?['has_sensitive_data'] ?? false) == true) {
      return 'Sensitive Data Found';
    }

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
      final phishingDetails = <String>[];

      if (phishing?['suspicious_urls'] != null && (phishing['suspicious_urls'] as List).isNotEmpty) {
        final urls = phishing['suspicious_urls'] as List;
        phishingDetails.add('${urls.length} suspicious URL${urls.length > 1 ? 's' : ''} found');
        for (int i = 0; i < urls.length && i < 3; i++) {
          phishingDetails.add('  • ${urls[i]}');
        }
        if (urls.length > 3) {
          phishingDetails.add('  • ... and ${urls.length - 3} more');
        }
      }
      if (phishing?['contains_urgency_keywords'] == true) {
        phishingDetails.add('Urgency indicators detected (e.g., "urgent", "immediate action required")');
      }
      if (phishing?['suspicious_sender'] == true) {
        phishingDetails.add('Suspicious sender domain detected');
      }
      if (phishing?['confidence'] != null) {
        phishingDetails.add('Detection confidence: ${(phishing['confidence'] * 100).toStringAsFixed(1)}%');
      }

      if (phishingDetails.isNotEmpty) {
        threats.add('🚨 Phishing Detected:\n${phishingDetails.join('\n')}');
      }
    }

    // Code injection details
    final codeInjection = results['code_injection'];
    if (codeInjection != null) {
      final status = codeInjection['status'];
      final confidence = codeInjection['confidence'];
      final details = codeInjection['details'];

      print('💉 DEBUG: Processing code injection details - status: $status, confidence: $confidence');

      if (status == 'Injection' || status == 'XSS' || (codeInjection['is_injection'] ?? false) == true) {
        final injectionDetails = <String>[];

        if (details != null && details is Map) {
          final patterns = details['patterns_found'] ?? details['detected_patterns'];
          if (patterns != null && patterns is List && patterns.isNotEmpty) {
            injectionDetails.add('${patterns.length} suspicious pattern${patterns.length > 1 ? 's' : ''} detected');
            for (int i = 0; i < patterns.length && i < 3; i++) {
              injectionDetails.add('  • ${patterns[i]}');
            }
            if (patterns.length > 3) {
              injectionDetails.add('  • ... and ${patterns.length - 3} more');
            }
          }
        }

        if (confidence != null) {
          injectionDetails.add('Detection confidence: ${(confidence * 100).toStringAsFixed(1)}%');
        }

        if (injectionDetails.isNotEmpty) {
          threats.add('💉 Code Injection Detected:\n${injectionDetails.join('\n')}');
          print('💉 DEBUG: Added code injection details to threats');
        }
      }
    }

    // Sensitive data details
    if (results['sensitive_data']?['classification'] != null &&
        results['sensitive_data']['classification'] != 'UNKNOWN' &&
        results['sensitive_data']['classification'] != 'ERROR' &&
        results['sensitive_data']['classification'] != 'NOT_SENSITIVE') {
      final sensitive = results['sensitive_data'];
      final sensitiveDetails = <String>[];

      if (sensitive?['classification'] != null) {
        sensitiveDetails.add('Data type: ${sensitive['classification']}');
      }
      if (sensitive?['confidence'] != null) {
        sensitiveDetails.add('Classification confidence: ${(sensitive['confidence'] * 100).toStringAsFixed(1)}%');
      }
      if (sensitive?['details'] != null) {
        sensitiveDetails.add('Details: ${sensitive['details']}');
      }

      if (sensitiveDetails.isNotEmpty) {
        threats.add('🔒 Sensitive Data Detected:\n${sensitiveDetails.join('\n')}');
      }
    }
    else if ((results['sensitive_data']?['has_sensitive_data'] ?? false) == true &&
             results['sensitive_data']?['classification'] != 'UNKNOWN' &&
             results['sensitive_data']?['classification'] != 'ERROR') {
      threats.add('🔒 Sensitive Data Detected: ${results['sensitive_data']['classification'] ?? 'Unknown type'}');
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

    if ((results['phishing']?['status'] == 'Phishing') || (results['phishing']?['is_phishing'] ?? false) == true) {
      actions.add('Do not click on any links in this content');
      actions.add('Verify the sender before taking any action');
      actions.add('Delete this message immediately');
    }

    final codeInjection = results['code_injection'];
    if (codeInjection != null && (codeInjection['status'] == 'Injection' || codeInjection['status'] == 'XSS' || (codeInjection['is_injection'] ?? false) == true)) {
      actions.add('Do not execute this code');
      actions.add('Review the input for suspicious patterns');
      actions.add('Use parameterized queries for database interactions');
    }

    final sensitiveData = results['sensitive_data'];
    final classification = sensitiveData?['classification'];
    if ((classification != null &&
         classification != 'Safe' &&
         classification != 'UNKNOWN' &&
         classification != 'ERROR' &&
         classification != 'NOT_SENSITIVE') ||
        (sensitiveData?['has_sensitive_data'] ?? false) == true) {
      actions.add('Remove or redact sensitive information before sharing');
      actions.add('Review data handling policies');
      actions.add('Consider encrypting this data if it needs to be stored');
    }

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

      print('📡 DEBUG: Raw analysis response:');
      print(jsonEncode(analysis));

      final result = ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        isThreat: _determineIsThreat(analysis),
        threatType: _determineThreatType(analysis),
        threatDetails: _generateThreatDetails(analysis),
        threatScore: analysis['overall_risk_score'],
        scannedContentPreview: text.length > 100 ? '${text.substring(0, 100)}...' : text,
        scanType: 'comprehensive',
        recommendedActions: _generateRecommendedActions(analysis),
        rawAnalysis: analysis,
      );

      print('🎯 DEBUG: Final ScanResult - isThreat: ${result.isThreat}, threatType: ${result.threatType}');
      print('🎯 DEBUG: Overall risk score: ${analysis['overall_risk_score']}');
      
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

      print('📡 DEBUG: Raw file analysis response:');
      print(jsonEncode(analysis));

      final result = ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        isThreat: _determineIsThreat(analysis),
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

      print('🎯 DEBUG: Final file ScanResult - isThreat: ${result.isThreat}, threatType: ${result.threatType}');
      print('🎯 DEBUG: File overall risk score: ${analysis['overall_risk_score']}');
      
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
  
  void clearHistory() {
    _scanHistory.clear();
    _lastScanResult = null;
    notifyListeners();
  }
  
  String _formatFileSize(int? bytes) {
    if (bytes == null) return '0 B';
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
  
  Future<Map<String, dynamic>?> encryptAndUploadFile(
    PlatformFile file,
    {double sensitivityScore = 0.5}
  ) async {
    if (file.bytes == null && file.path == null) {
      _error = 'Selected file is empty or invalid';
      notifyListeners();
      return null;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final apiService = ApiService();
      
      List<int> fileBytes;
      if (file.bytes != null) {
        fileBytes = file.bytes!;
      } else if (file.path != null) {
        fileBytes = await File(file.path!).readAsBytes();
      } else {
        throw Exception('No file data available');
      }

      final result = await apiService.encryptAndUploadFile(
        fileBytes,
        file.name,
        sensitivityScore: sensitivityScore,
      );

      return result;
    } catch (e) {
      _error = 'Failed to encrypt and upload file: ${e.toString()}';
      debugPrint('Encrypt and upload error: $_error');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  List<Map<String, dynamic>> _fileHistory = [];
  List<Map<String, dynamic>> get fileHistory => _fileHistory;

  Future<void> fetchFileHistory() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final history = await _apiService.getFileHistory();
      _fileHistory = List<Map<String, dynamic>>.from(history);
    } catch (e) {
      _error = 'Failed to fetch file history: $e';
      debugPrint('File history error: $_error');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Uint8List?> downloadFile(String firestoreDocId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      return await _apiService.downloadAndDecryptFile(firestoreDocId);
    } catch (e) {
      _error = 'Failed to download file: $e';
      debugPrint('File download error: $_error');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}