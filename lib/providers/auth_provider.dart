import 'package:flutter/foundation.dart';

class AuthProvider with ChangeNotifier {
  String? _token;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;

  String? get token => _token;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  // Mock Login - Always succeeds for now
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    // Mock authentication - always succeeds
    if (email.isNotEmpty && password.isNotEmpty) {
      _token = 'mock_token_${DateTime.now().millisecondsSinceEpoch}';
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    }

    _errorMessage = 'Please enter valid credentials';
    _isLoading = false;
    notifyListeners();
    return false;
  }

  // Mock SignIn - Alias for login (for compatibility)
  Future<bool> signIn(String email, String password) async {
    return await login(email, password);
  }

  // Mock Signup - Always succeeds for now
  Future<bool> signup(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    // Mock signup - always succeeds
    if (email.isNotEmpty && password.isNotEmpty) {
      _token = 'mock_token_${DateTime.now().millisecondsSinceEpoch}';
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    }

    _errorMessage = 'Please enter valid information';
    _isLoading = false;
    notifyListeners();
    return false;
  }

  // Logout method
  void logout() {
    _token = null;
    _isAuthenticated = false;
    _errorMessage = null;
    notifyListeners();
  }

  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}