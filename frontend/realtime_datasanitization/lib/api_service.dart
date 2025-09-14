import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String _baseUrl = "https://cybersecurity-api-service-44185828496.us-central1.run.app/"; 

  // Example for GET request to the root endpoint
  Future<String> getRoot() async {
    final response = await http.get(Uri.parse(_baseUrl));

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['message'];
    } else {
      throw Exception('Failed to load welcome message');
    }
  }

  // Example for POST request to /analyze-text
  Future<Map<String, dynamic>> analyzeText(String text) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/analyze-text'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'text': text,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to analyze text');
    }
  }
}