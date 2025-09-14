// screens/threat_detection.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lottie/lottie.dart';
import 'dart:math';
import '../providers/threat_provider.dart';

class ThreatDetectionScreen extends StatefulWidget {
  const ThreatDetectionScreen({Key? key}) : super(key: key);

  @override
  _ThreatDetectionScreenState createState() => _ThreatDetectionScreenState();
}

class _ThreatDetectionScreenState extends State<ThreatDetectionScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _textController = TextEditingController();
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutQuart,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _textController.dispose();
    super.dispose();
  }

  Widget _buildAnalysisCard(String title, String value, Color color) {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      color: Colors.grey[900],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                color: Colors.grey[400],
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThreatProvider>(
      builder: (context, provider, _) {
        return Scaffold(
          backgroundColor: const Color(0xFF0A0E1A),
          body: SafeArea(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SlideTransition(
                  position: _slideAnimation,
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Threat Analysis',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 30),
                        
                        // Input Card
                        Card(
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                          color: const Color(0xFF1A1F33),
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              children: [
                                TextField(
                                  controller: _textController,
                                  style: const TextStyle(color: Colors.white),
                                  decoration: InputDecoration(
                                    hintText: 'Enter text or URL to analyze...',
                                    hintStyle: TextStyle(color: Colors.grey[500]),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(12),
                                      borderSide: BorderSide.none,
                                    ),
                                    filled: true,
                                    fillColor: const Color(0xFF252A3D),
                                    contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 20,
                                      vertical: 16,
                                    ),
                                  ),
                                  maxLines: 3,
                                  minLines: 1,
                                ),
                                const SizedBox(height: 16),
                                Row(
                                  children: [
                                    Expanded(
                                      child: AnimatedContainer(
                                        duration: const Duration(milliseconds: 300),
                                        height: 50,
                                        child: ElevatedButton(
                                          onPressed: provider.isLoading
                                              ? null
                                              : () {
                                                  if (_textController.text.isNotEmpty) {
                                                    provider.performTextAnalysis(_textController.text);
                                                  }
                                                },
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(0xFF6C63FF),
                                            shape: RoundedRectangleBorder(
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            elevation: 2,
                                            padding: const EdgeInsets.symmetric(vertical: 12),
                                          ),
                                          child: provider.isLoading
                                              ? const SizedBox(
                                                  width: 20,
                                                  height: 20,
                                                  child: CircularProgressIndicator(
                                                    strokeWidth: 2,
                                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                                  ),
                                                )
                                              : const Text(
                                                  'Analyze Text',
                                                  style: TextStyle(
                                                    fontSize: 16,
                                                    fontWeight: FontWeight.w600,
                                                  ),
                                                ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Container(
                                      height: 50,
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF252A3D),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: TextButton.icon(
                                        onPressed: provider.isLoading
                                            ? null
                                            : () {
                                                provider.performFileAnalysis();
                                              },
                                        icon: const Icon(Icons.upload_file, color: Colors.white70),
                                        label: const Text(
                                          'Upload File',
                                          style: TextStyle(color: Colors.white70),
                                        ),
                                        style: TextButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(horizontal: 16),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 30),
                        
                        // Results Section
                        if (provider.analysisResult != null) ..._buildResults(provider.analysisResult!),
                        
                        // Empty State
                        if (provider.analysisResult == null && !provider.isLoading)
                          Column(
                            children: [
                              Lottie.asset(
                                'assets/scanning.json', // Add this asset to your project
                                width: 250,
                                height: 250,
                                fit: BoxFit.cover,
                              ),
                              const SizedBox(height: 20),
                              const Text(
                                'Enter text or upload a file to analyze for threats',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.grey,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                        
                        // Loading State
                        if (provider.isLoading)
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 40),
                            child: Column(
                              children: [
                                Lottie.asset(
                                  'assets/scanning.json', // Add this asset to your project
                                  width: 200,
                                  height: 200,
                                  fit: BoxFit.cover,
                                ),
                                const SizedBox(height: 20),
                                const Text(
                                  'Analyzing content...',
                                  style: TextStyle(
                                    color: Colors.white70,
                                    fontSize: 18,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
  
  List<Widget> _buildResults(Map<String, dynamic> results) {
    return [
      const Text(
        'Analysis Results',
        style: TextStyle(
          color: Colors.white,
          fontSize: 22,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
      const SizedBox(height: 20),
      GridView.count(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.5,
        children: [
          _buildAnalysisCard(
            'Threat Level',
            results['threat_level']?.toString().toUpperCase() ?? 'UNKNOWN',
            _getThreatColor(results['threat_level']?.toString().toLowerCase() ?? ''),
          ),
          _buildAnalysisCard(
            'Confidence',
            '${results['confidence']?.toStringAsFixed(1) ?? '0'}%',
            _getConfidenceColor(double.tryParse(results['confidence']?.toString() ?? '0') ?? 0),
          ),
          if (results['threat_type'] != null)
            _buildAnalysisCard(
              'Threat Type',
              results['threat_type'].toString().toUpperCase(),
              Colors.orange,
            ),
          if (results['is_malicious'] != null)
            _buildAnalysisCard(
              'Status',
              results['is_malicious'] == true ? 'MALICIOUS' : 'SAFE',
              results['is_malicious'] == true ? Colors.red : Colors.green,
            ),
        ],
      ),
      const SizedBox(height: 20),
      if (results['details'] != null)
        Card(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
          color: const Color(0xFF1A1F33),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Detailed Analysis',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                if (results['details'] is Map)
                  ..._buildDetailItems(results['details'] as Map<String, dynamic>)
                else
                  Text(
                    results['details'].toString(),
                    style: const TextStyle(color: Colors.white70, height: 1.5),
                  ),
              ],
            ),
          ),
        ),
    ];
  }
  
  List<Widget> _buildDetailItems(Map<String, dynamic> details) {
    return details.entries.map((entry) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 4.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '• ${entry.key.replaceAll('_', ' ').toUpperCase()}: ',
              style: const TextStyle(
                color: Colors.white70,
                fontWeight: FontWeight.bold,
              ),
            ),
            Expanded(
              child: Text(
                entry.value.toString(),
                style: const TextStyle(color: Colors.white70),
              ),
            ),
          ],
        ),
      );
    }).toList();
  }
  
  Color _getThreatColor(String level) {
    switch (level.toLowerCase()) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.yellow;
      default:
        return Colors.grey;
    }
  }
  
  Color _getConfidenceColor(double confidence) {
    if (confidence > 75) return Colors.green;
    if (confidence > 50) return Colors.lightGreen;
    if (confidence > 25) return Colors.orange;
    return Colors.red;
  }
}