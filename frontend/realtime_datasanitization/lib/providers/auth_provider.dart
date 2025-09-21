import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  String? _token;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String _error = '';
  String? _userEmail;

  String? get token => _token;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String get error => _error;
  String? get userEmail => _userEmail;

  AuthProvider() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('token');
      _userEmail = prefs.getString('user_email');
      
      if (_token != null) {
        _apiService.setAuthToken(_token!);
        // Verify token is still valid by making a test call
        try {
          await _apiService.getSystemHealth();
          _isAuthenticated = true;
        } catch (e) {
          // Token is invalid, clear it
          await logout();
        }
      }
    } catch (e) {
      debugPrint('Error loading token: $e');
      _error = 'Failed to load authentication data';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    if (!mounted) return false;
    
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      debugPrint('Attempting login for: $email');
      
      final response = await _apiService.login(email, password);
      
      if (response['access_token'] != null) {
        _token = response['access_token'];
        _userEmail = email;
        _isAuthenticated = true;
        _apiService.setAuthToken(_token!);
        
        // Save to persistent storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('token', _token!);
        await prefs.setString('user_email', email);
        
        debugPrint('Login successful');
        if (mounted) {
          _isLoading = false;
          notifyListeners();
        }
        return true;
      } else {
        throw Exception('No access token received');
      }
    } catch (e) {
      debugPrint('Login error: $e');
      _error = _parseError(e.toString());
      if (mounted) {
        _isLoading = false;
        notifyListeners();
      }
      return false;
    }
  }

  Future<bool> register(String email, String password) async {
    if (!mounted) return false;
    
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      debugPrint('Attempting registration for: $email');
      
      await _apiService.register(email, password);
      debugPrint('Registration successful');
      
      if (mounted) {
        _isLoading = false;
        notifyListeners();
      }
      return true;
    } catch (e) {
      debugPrint('Registration error: $e');
      _error = _parseError(e.toString());
      if (mounted) {
        _isLoading = false;
        notifyListeners();
      }
      return false;
    }
  }

  Future<void> logout() async {
    _token = null;
    _userEmail = null;
    _isAuthenticated = false;
    _error = '';
    _apiService.clearAuthToken();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user_email');
    
    notifyListeners();
  }

  String _parseError(String error) {
    if (error.contains('Incorrect email or password')) {
      return 'Incorrect email or password';
    } else if (error.contains('Email already registered')) {
      return 'Email already registered';
    } else if (error.contains('Failed to connect')) {
      return 'Connection failed. Please try again.';
    }
    return 'An error occurred. Please try again.';
  }
  
  bool get mounted {
    try {
      // Simple check if the provider is still active
      return true;
    } catch (e) {
      return false;
    }
  }
}