import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  String? _token;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String _error = '';

  String? get token => _token;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String get error => _error;

  AuthProvider() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
    if (_token != null) {
      _isAuthenticated = true;
      _apiService.setAuthToken(_token!);
    }
    notifyListeners();
  }

  Future<bool> login(String email, String password) async { // 👈 CHANGED
  _isLoading = true;
  _error = '';
  notifyListeners();

  try {
    final response = await _apiService.login(email, password); // 👈 CHANGED
    _token = response['access_token'];
    _isAuthenticated = true;
    _apiService.setAuthToken(_token!);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', _token!);
    _isLoading = false;
    notifyListeners();
    return true;
  } catch (e) {
    _error = e.toString();
    _isLoading = false;
    notifyListeners();
    return false;
  }
}

  Future<bool> register(String email, String password) async { // 👈 CHANGED
  _isLoading = true;
  _error = '';
  notifyListeners();

  try {
    await _apiService.register(email, password); // 👈 CHANGED
    _isLoading = false;
    notifyListeners();
    return true;
  } catch (e) {
    _error = e.toString();
    _isLoading = false;
    notifyListeners();
    return false;
  }
}

  Future<void> logout() async {
    _token = null;
    _isAuthenticated = false;
    _apiService.clearAuthToken();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    notifyListeners();
  }
}
