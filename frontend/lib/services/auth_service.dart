import 'package:flutter/foundation.dart';
import 'package:firebase_auth/firebase_auth.dart';

enum AuthStatus {
  uninitialized,
  authenticating,
  authenticated,
  unauthenticated,
}

class AuthService with ChangeNotifier {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  User? _user;
  AuthStatus _status = AuthStatus.uninitialized;

  AuthService() {
    _status = AuthStatus.authenticating;
    notifyListeners();
    _auth.authStateChanges().listen((User? user) {
      _user = user;
      _status = user == null
          ? AuthStatus.unauthenticated
          : AuthStatus.authenticated;
      notifyListeners();
    });
  }

  User? get user => _user;
  AuthStatus get status => _status;
  bool get isUserLoggedIn => _status == AuthStatus.authenticated;

  Future<void> signUp(String email, String password) async {
    try {
      await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (_) {
      rethrow;
    }
  }

  Future<void> login(String email, String password) async {
    try {
      await _auth.signInWithEmailAndPassword(email: email, password: password);
    } on FirebaseAuthException catch (_) {
      rethrow;
    }
  }

  Future<String?> getIdToken() async {
    return await _user?.getIdToken();
  }

  Future<void> logout() async {
    await _auth.signOut();
  }
}
