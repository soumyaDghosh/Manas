import 'package:flutter/material.dart';

class StartView extends StatelessWidget {
  final VoidCallback onStartSession;

  const StartView({super.key, required this.onStartSession});

  @override
  Widget build(BuildContext context) {
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: isLandscape
            ? Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const _AvatarSection(),
                  const SizedBox(width: 40),
                  Expanded(
                    child: _TextAndButton(onStartSession: onStartSession),
                  ),
                ],
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const _AvatarSection(),
                  const SizedBox(height: 24),
                  _TextAndButton(onStartSession: onStartSession),
                ],
              ),
      ),
    );
  }
}

class _AvatarSection extends StatelessWidget {
  const _AvatarSection();

  @override
  Widget build(BuildContext context) {
    return const CircleAvatar(
      radius: 50,
      backgroundColor: Color(0xFF160842),
      child: Icon(Icons.smart_toy_outlined, size: 50, color: Colors.white),
    );
  }
}

class _TextAndButton extends StatelessWidget {
  final VoidCallback onStartSession;
  const _TextAndButton({required this.onStartSession});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text(
          'Welcome to Manas',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        Text(
          "Your mind's safe space. Start a new session to begin.",
          style: TextStyle(fontSize: 16, color: Colors.grey.shade700),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        ElevatedButton.icon(
          icon: const Icon(Icons.play_arrow),
          label: const Text("Start New Session"),
          onPressed: onStartSession,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF38005f),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            textStyle: const TextStyle(fontSize: 18),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(30),
            ),
          ),
        ),
      ],
    );
  }
}
