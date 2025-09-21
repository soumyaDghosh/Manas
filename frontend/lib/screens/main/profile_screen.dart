import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _notificationToggle = false;
  bool _checkInsToggle = false;
  bool _isSigningOut = false;

  Future<void> _handleLogout() async {
    setState(() => _isSigningOut = true);
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      await authService.logout();
      if (mounted) {
        Navigator.of(
          context,
        ).pushNamedAndRemoveUntil('/signIn', (Route<dynamic> route) => false);
      }
    } catch (e) {
      // Handle error
    } finally {
      if (mounted) {
        setState(() => _isSigningOut = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Settings',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  Text('Manage Your preferences'),
                ],
              ),
              ElevatedButton(
                onPressed: _isSigningOut ? null : _handleLogout,
                child: Text(_isSigningOut ? 'Signing out...' : 'Sign Out'),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildSettingsCard(
            title: 'Notifications',
            children: [
              _buildToggleRow(
                'Enable Notifications',
                _notificationToggle,
                (value) => setState(() => _notificationToggle = value),
              ),
              const Divider(),
              _buildToggleRow(
                'Enable Check-Ins',
                _checkInsToggle,
                (value) => setState(() => _checkInsToggle = value),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildSettingsCard(
            title: 'About Manas',
            children: const [
              Text(
                "Manas is your personal AI companion for mental wellness. I'm here to provide emotional support, help you process your thoughts and offer a safe space for reflection.",
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsCard({
    required String title,
    required List<Widget> children,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildToggleRow(
    String title,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: const TextStyle(fontSize: 16)),
        Switch(value: value, onChanged: onChanged),
      ],
    );
  }
}
