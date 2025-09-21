import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/message.dart';
import '../services/auth_service.dart';
import '../services/chat_service.dart';

class ChatViewModel extends ChangeNotifier {
  final AuthService _authService;
  final ChatService _chatService;

  ChatViewModel({
    required AuthService authService,
    required ChatService chatService,
  }) : _authService = authService,
       _chatService = chatService;

  List<Message> _chat = [];
  bool _isLoading = false;
  bool _isSessionActive = false;
  Timer? _sessionTimer;

  List<Message> get chat => _chat;
  bool get isLoading => _isLoading;
  bool get isSessionActive => _isSessionActive;

  void startSession() {
    _chat = [
      Message(
        sender: MessageSender.bot,
        text: "Hello! How can I help you today?",
      ),
    ];
    _isSessionActive = true;
    _resetSessionTimer();
    notifyListeners();
  }

  Future<void> endSession({bool autoEnded = false}) async {
    if (!_isSessionActive) return;

    _sessionTimer?.cancel();
    final token = await _authService.getIdToken();
    if (token != null) {
      await _chatService.endSession(token: token);
    }

    final endMessage = autoEnded
        ? "Session ended due to inactivity."
        : "Session has ended. Start a new one anytime!";
    _chat.add(Message(sender: MessageSender.bot, text: endMessage));
    _isSessionActive = false;
    _isLoading = false;
    notifyListeners();
  }

  void _resetSessionTimer() {
    _sessionTimer?.cancel();
    _sessionTimer = Timer(const Duration(minutes: 10), () {
      endSession(autoEnded: true);
    });
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty || !_isSessionActive) return;

    _resetSessionTimer();
    _chat.add(Message(sender: MessageSender.user, text: text));
    _isLoading = true;
    notifyListeners();

    try {
      final token = await _authService.getIdToken();
      if (token == null) throw Exception('Authentication token not found.');

      final reply = await _chatService.processMessage(text: text, token: token);
      _chat.add(Message(sender: MessageSender.bot, text: reply));
      _resetSessionTimer();
    } catch (e) {
      _chat.add(
        Message(sender: MessageSender.bot, text: "Oops! Something went wrong."),
      );
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _sessionTimer?.cancel();
    super.dispose();
  }
}
