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
  int get totalThreatsDetected => _scanHistory.where((r) => r.isThreat).length;
  
  // Clear any error state
  void clearError() {
    if (_error != null) {
      _error = null;
      notifyListeners();
    }
  }

  /// Analyze text for potential threats
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
      // In a real app, this would call your API service
      // For now, we'll simulate an API call with mock data
      await Future.delayed(const Duration(seconds: 1));
      
      // Simulate analysis logic
      final bool isThreat = _simulateThreatDetection(text);
      final result = ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        isThreat: isThreat,
        threatType: isThreat ? 'suspicious_content' : null,
        threatDetails: isThreat ? 'The text contains potentially suspicious patterns' : null,
        threatScore: isThreat ? 0.85 : 0.1,
        scannedContentPreview: text.length > 100 ? '${text.substring(0, 100)}...' : text,
        scanType: 'text',
        recommendedActions: isThreat 
            ? ['Review the content', 'Contact security team if unsure'] 
            : ['No action required'],
      );
      
      _lastScanResult = result;
      _scanHistory.insert(0, result);
      return result;
      
    } catch (e) {
      _error = 'Failed to analyze text: ${e.toString()}';
      debugPrint('Text analysis error: $_error');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Analyze a file for potential threats
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
      // In a real app, this would upload the file to your API
      // For now, we'll simulate an API call with mock data
      await Future.delayed(const Duration(seconds: 2));
      
      // Get file extension safely
      final fileName = file.name;
      final fileExt = fileName.contains('.') 
          ? fileName.split('.').last.toLowerCase() 
          : 'unknown';
      
      final isExecutable = ['exe', 'dll', 'js', 'vbs', 'ps1', 'bat', 'sh'].contains(fileExt);
      final isDocument = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].contains(fileExt);
      final isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].contains(fileExt);
      
      // Check file size (in bytes)
      final fileSize = file.size;
      final isLargeFile = fileSize > 10 * 1024 * 1024; // 10MB
      
      final isThreat = isExecutable || (isDocument && file.size! > 10 * 1024 * 1024); // >10MB docs are suspicious
      
      final result = ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        isThreat: isThreat,
        threatType: isThreat ? (isExecutable ? 'executable_file' : 'suspicious_document') : null,
        threatDetails: isThreat 
            ? (isExecutable 
                ? 'Executable files can contain malicious code' 
                : 'Document is unusually large and may contain embedded threats')
            : null,
        threatScore: isThreat ? (isExecutable ? 0.95 : 0.7) : 0.1,
        scannedContentPreview: 'File: ${file.name} (${_formatFileSize(file.size)})',
        scanType: 'file',
        recommendedActions: isThreat 
            ? ['Do not open the file', 'Scan with antivirus', 'Delete if not needed'] 
            : ['File appears to be safe'],
        metadata: {
          'filename': file.name,
          'size': file.size,
          'extension': fileExt,
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