import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final ApiService _apiService;
  User? _user;

  User? get user => _user;
  bool get isAuthenticated => _user != null;

  AuthService(this._apiService) {
    _auth.authStateChanges().listen((User? user) async {
      _user = user;
      if (user != null) {
        // Sync with backend on auth state change (login/startup)
        await _syncWithBackend();
      }
      notifyListeners();
    });
  }

  Future<void> signInAnonymously() async {
    try {
      await _auth.signInAnonymously();
    } catch (e) {
      print("Error signing in anonymously: $e");
    }
  }

  // Future<void> signInWithGoogle() async { ... } (Omitted for brevity, standard implementation)

  Future<void> signOut() async {
    await _auth.signOut();
  }

  Future<void> _syncWithBackend() async {
    if (_user == null) return;
    try {
      final token = await _user!.getIdToken();
      // We pass the token to the API service to sync
      if (token != null) {
        await _apiService.syncUser(token);
      }
    } catch (e) {
      print("Sync failed: $e");
    }
  }
  
  Future<String?> getIdToken() async {
    if (_user == null) return null;
    return await _user!.getIdToken();
  }
}
