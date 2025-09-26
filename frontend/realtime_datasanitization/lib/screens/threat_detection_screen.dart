import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../providers/threat_provider.dart';
import '../models/scan_result.dart';

class ThreatDetectionScreen extends StatefulWidget {
  const ThreatDetectionScreen({super.key});

  @override
  State<ThreatDetectionScreen> createState() => _ThreatDetectionScreenState();
}

class _ThreatDetectionScreenState extends State<ThreatDetectionScreen> {
  final TextEditingController _textController = TextEditingController();
  bool _isAnalyzing = false;
  PlatformFile? _selectedFile;
  ScanResult? _scanResult;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.any,
        allowMultiple: false,
      );

      if (result != null) {
        setState(() {
          _selectedFile = result.files.single;
          _scanResult = null;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error selecting file: $e')),
        );
      }
    }
  }

  Future<void> _analyzeContent() async {
    if (_textController.text.isEmpty && _selectedFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter text or select a file')),
      );
      return;
    }

    setState(() {
      _isAnalyzing = true;
    });

    try {
      final threatProvider = context.read<ThreatProvider>();
      
      if (_textController.text.isNotEmpty) {
        // Analyze text
        _scanResult = await threatProvider.analyzeText(_textController.text);
      } else if (_selectedFile != null) {
        // Analyze file
        _scanResult = await threatProvider.analyzeFile(_selectedFile!);
      }

      if (mounted) {
        setState(() {});
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error analyzing content: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Threat Detection'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              // TODO: Navigate to scan history
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Text input
            TextField(
              controller: _textController,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'Enter text to analyze',
                border: OutlineInputBorder(),
                hintText: 'Paste suspicious text here...',
              ),
              onChanged: (value) {
                if (value.isNotEmpty) {
                  setState(() {
                    _selectedFile = null;
                    _scanResult = null;
                  });
                }
              },
            ),
            
            const SizedBox(height: 16),
            
            // Or divider
            const Row(
              children: [
                Expanded(child: Divider()),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8.0),
                  child: Text('OR'),
                ),
                Expanded(child: Divider()),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // File picker
            ElevatedButton.icon(
              onPressed: _pickFile,
              icon: const Icon(Icons.attach_file),
              label: Text(_selectedFile == null 
                  ? 'Select a file to analyze' 
                  : 'Selected: ${_selectedFile?.name}'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Analyze button
            ElevatedButton(
              onPressed: _isAnalyzing ? null : _analyzeContent,
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).primaryColor,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isAnalyzing
                  ? const CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    )
                  : const Text(
                      'ANALYZE FOR THREATS',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),
            
            const SizedBox(height: 32),
            
            // Results
            if (_scanResult != null) _buildScanResult(_scanResult!)
            else if (_isAnalyzing)
              const Center(child: CircularProgressIndicator())
            else
              const Column(
                children: [
                  Icon(
                    Icons.security,
                    size: 64,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'No analysis results yet',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Enter text or select a file to analyze for security threats',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildScanResult(ScanResult result) {
    final bool isThreat = result.isThreat;
    final analysis = result.rawAnalysis ?? {};
    final analyses = analysis['results'] ?? {};
    final modelArtifacts = analysis['model_artifacts_used'] ?? {};
    final fileMetadata = analysis['file_metadata'];

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isThreat ? Colors.red : Colors.green,
          width: 2,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Overall Risk Section
            Row(
              children: [
                Icon(
                  isThreat ? Icons.warning_amber : Icons.check_circle,
                  color: isThreat ? Colors.orange : Colors.green,
                  size: 36,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isThreat ? 'Potential Threat Detected!' : 'No Threats Found',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (analysis['overall_risk_score'] != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Risk Level: ${_getRiskLevel(analysis['overall_risk_score'])}',
                          style: TextStyle(
                            fontSize: 14,
                            color: isThreat ? Colors.red : Colors.green,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                      if (modelArtifacts.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          'AI Models Used: ${modelArtifacts.values.where((used) => used == true).length}/${modelArtifacts.length}',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Risk Score Bar
            if (analysis['overall_risk_score'] != null) ...[
              LinearProgressIndicator(
                value: analysis['overall_risk_score'],
                backgroundColor: Colors.grey[300],
                valueColor: AlwaysStoppedAnimation<Color>(
                  _getRiskColor(analysis['overall_risk_score'])
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Risk Score: ${analysis['overall_risk_score'].toStringAsFixed(2)}',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: _getRiskColor(analysis['overall_risk_score']),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // File Information (if applicable)
            if (fileMetadata != null) ...[
              const Text(
                'File Information:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              const SizedBox(height: 8),
              Text('Filename: ${fileMetadata['filename']}'),
              Text('Size: ${_formatFileSize(fileMetadata['size'])}'),
              Text('Type: ${fileMetadata['content_type'] ?? 'Unknown'}'),
              if (analyses['file_analysis'] != null) ...[
                Text('SHA-256: ${analyses['file_analysis']['file_hash']?.substring(0, 16)}...'),
              ],
              const SizedBox(height: 16),
            ],

            if (isThreat) ...[
              const Text(
                'Threat Details:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
              const SizedBox(height: 8),
              Text(result.threatDetails ?? 'No additional details available'),
              const SizedBox(height: 16),
            ],

            // Detailed Analysis Sections
            _buildAnalysisSection(
              title: 'Sensitive Data Analysis',
              analysis: analyses['sensitive_data'] ?? {},
              modelUsed: modelArtifacts['sensitive_data_model'] ?? false,
            ),

            _buildAnalysisSection(
              title: 'Phishing Detection',
              analysis: analyses['phishing'] ?? {},
              modelUsed: modelArtifacts['phishing_model'] ?? false,
            ),

            _buildAnalysisSection(
              title: 'Code Injection Analysis',
              analysis: analyses['code_injection'] ?? {},
              modelUsed: modelArtifacts['code_injection_model'] ?? false,
            ),

            _buildAnalysisSection(
              title: 'Data Quality Assessment',
              analysis: analyses['data_quality'] ?? {},
              modelUsed: modelArtifacts['data_quality_model'] ?? false,
            ),

            // File-specific analysis
            if (analyses['file_analysis'] != null) ...[
              _buildAnalysisSection(
                title: 'File Analysis',
                analysis: analyses['file_analysis'],
                modelUsed: true,
              ),
            ],

            // Alerts Created
            if (analysis['alerts_created'] != null && (analysis['alerts_created'] as List).isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Security Alerts Created:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              ... (analysis['alerts_created'] as List).map((alert) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2.0),
                    child: Row(
                      children: [
                        const Icon(Icons.notification_important, size: 16, color: Colors.orange),
                        const SizedBox(width: 4),
                        Text(
                          alert.toString().replaceAll('_', ' ').toUpperCase(),
                          style: const TextStyle(color: Colors.orange),
                        ),
                      ],
                    ),
                  )).toList(),
            ],

            // Recommended Actions
            if (result.recommendedActions.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Recommended Actions:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              ...result.recommendedActions.map((action) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.arrow_right, size: 20),
                        const SizedBox(width: 4),
                        Expanded(child: Text(action)),
                      ],
                    ),
                  )).toList(),
            ],

            const SizedBox(height: 16),

            // Additional metadata
            if (result.timestamp != null) ...[
              const Divider(),
              Text(
                'Scanned on: ${_formatDateTime(result.timestamp!)}',
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildAnalysisSection({required String title, required Map<String, dynamic> analysis, bool modelUsed = false}) {
    return ExpansionTile(
      title: Row(
        children: [
          Text(
            title,
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: modelUsed ? Colors.green.shade100 : Colors.orange.shade100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: modelUsed ? Colors.green : Colors.orange,
                width: 1,
              ),
            ),
            child: Text(
              modelUsed ? 'AI Model' : 'Basic',
              style: TextStyle(
                fontSize: 10,
                color: modelUsed ? Colors.green.shade800 : Colors.orange.shade800,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: _buildAnalysisDetails(analysis),
        ),
      ],
    );
  }

  Widget _buildAnalysisDetails(Map<String, dynamic> analysis) {
    if (analysis.isEmpty) {
      return const Text('No data available');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: analysis.entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${entry.key}: ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Expanded(
                child: Text(
                  entry.value.toString(),
                  softWrap: true,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  String _getRiskLevel(double score) {
    if (score >= 0.8) return 'Critical';
    if (score >= 0.6) return 'High';
    if (score >= 0.4) return 'Medium';
    if (score >= 0.2) return 'Low';
    return 'Info';
  }

  Color _getRiskColor(double score) {
    if (score >= 0.8) return Colors.red;
    if (score >= 0.6) return Colors.orange;
    if (score >= 0.4) return Colors.amber;
    if (score >= 0.2) return Colors.lightBlue;
    return Colors.green;
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  String _formatFileSize(dynamic size) {
    if (size == null) return 'Unknown';

    double bytes = 0;
    if (size is int) {
      bytes = size.toDouble();
    } else if (size is double) {
      bytes = size;
    } else if (size is String) {
      bytes = double.tryParse(size) ?? 0;
    }

    if (bytes == 0) return '0 B';

    const suffixes = ['B', 'KB', 'MB', 'GB', 'TB'];
    var i = 0;
    while (bytes >= 1024 && i < suffixes.length - 1) {
      bytes /= 1024;
      i++;
    }

    return '${bytes.toStringAsFixed(1)} ${suffixes[i]}';
  }
}
