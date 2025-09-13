import 'package:flutter/material.dart';

class AuthProvider extends ChangeNotifier {
  bool _isLoading = false;
  String? _errorMessage;
  bool _isAuthenticated = false;
  String _userName = 'User';

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _isAuthenticated;
  String get userName => _userName;

  Future<bool> signIn(String email, String password) async {
    _setLoading(true);
    await Future.delayed(Duration(milliseconds: 500)); // Simulate API call
    
    // Extract username from email
    _userName = email.split('@')[0];
    _isAuthenticated = true;
    _setLoading(false);
    return true;
  }

  Future<bool> signUp(String email, String password) async {
    _setLoading(true);
    await Future.delayed(Duration(milliseconds: 500)); // Simulate API call
    
    // Extract username from email
    _userName = email.split('@')[0];
    _isAuthenticated = true;
    _setLoading(false);
    return true;
  }

  Future<void> signOut() async {
    _isAuthenticated = false;
    _userName = 'User';
    notifyListeners();
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}