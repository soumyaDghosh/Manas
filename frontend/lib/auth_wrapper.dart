import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/landing_screen.dart';
import 'screens/layout_screen.dart';
import 'services/auth_service.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = context.watch<AuthService>();

    switch (authService.status) {
      case AuthStatus.unauthenticated:
        return const LandingScreen();
      case AuthStatus.authenticated:
        return const LayoutScreen();
      case AuthStatus.authenticating:
      case AuthStatus.uninitialized:
      // ignore: unreachable_switch_default
      default:
        return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
  }
}
