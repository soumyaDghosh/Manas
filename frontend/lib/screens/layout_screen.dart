import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/auth_service.dart';
import '../services/chat_service.dart';
import '../services/journal_service.dart';
import '../views/chat_viewmodel.dart';
import '../views/journal_viewmodel.dart';
import 'main/chat_screen.dart';
import 'main/journal_screen.dart';
import 'main/profile_screen.dart';

class LayoutScreen extends StatelessWidget {
  const LayoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (context) => ChatViewModel(
            authService: context.read<AuthService>(),
            chatService: ChatService(),
          ),
        ),
        ChangeNotifierProvider(
          create: (context) => JournalViewModel(
            authService: context.read<AuthService>(),
            journalService: JournalService(),
          ),
        ),
      ],
      child: const _LayoutView(),
    );
  }
}

class _LayoutView extends StatefulWidget {
  const _LayoutView();

  @override
  State<_LayoutView> createState() => _LayoutViewState();
}

class _LayoutViewState extends State<_LayoutView> {
  int _selectedIndex = 0;

  static const List<Widget> _screens = <Widget>[
    ChatScreen(),
    JournalScreen(),
    ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<JournalViewModel>().fetchJournals();
    });
  }

  void _onItemTapped(int index) {
    if (index == 1) {
      context.read<JournalViewModel>().fetchJournals();
    }
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF100040),
        elevation: 0,
        automaticallyImplyLeading: false,

        title: Row(
          children: [
            Image.asset('assets/RoboIcon.png', height: 32),
            const SizedBox(width: 12),
            const Text(
              'MANAS',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),

        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(
                  Icons.notifications_outlined,
                  color: Colors.white,
                  size: 28,
                ),
                onPressed: () {},
              ),
              Positioned(
                top: 10,
                right: 10,
                child: Container(
                  height: 10,
                  width: 10,
                  decoration: BoxDecoration(
                    color: Colors.greenAccent.shade400,
                    shape: BoxShape.circle,
                    border: Border.all(
                      width: 1.5,
                      color: const Color(0xFF100040),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: IndexedStack(index: _selectedIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Chat'),
          BottomNavigationBarItem(icon: Icon(Icons.book), label: 'Journal'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      ),
    );
  }
}
