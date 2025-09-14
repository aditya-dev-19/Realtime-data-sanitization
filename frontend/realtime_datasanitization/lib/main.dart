import 'package:flutter/material.dart';
import 'api_service.dart'; // Import your ApiService

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cybersecurity App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final ApiService _apiService = ApiService();
  final TextEditingController _textController = TextEditingController();
  String _welcomeMessage = 'Loading...';
  Map<String, dynamic>? _analysisResult;

  @override
  void initState() {
    super.initState();
    _loadWelcomeMessage();
  }

  void _loadWelcomeMessage() async {
    try {
      final message = await _apiService.getRoot();
      setState(() {
        _welcomeMessage = message;
      });
    } catch (e) {
      setState(() {
        _welcomeMessage = 'Failed to load message';
      });
    }
  }

  void _analyzeText() async {
    if (_textController.text.isEmpty) return;

    try {
      final result = await _apiService.analyzeText(_textController.text);
      setState(() {
        _analysisResult = result;
      });
    } catch (e) {
      // Handle error, maybe show a snackbar
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cybersecurity Analysis'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              _welcomeMessage,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _textController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Enter text to analyze',
              ),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _analyzeText,
              child: const Text('Analyze Text'),
            ),
            const SizedBox(height: 20),
            if (_analysisResult != null)
              Expanded(
                child: SingleChildScrollView(
                  child: Text(
                    const JsonEncoder.withIndent('  ').convert(_analysisResult),
                    style: const TextStyle(fontFamily: 'monospace'),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}