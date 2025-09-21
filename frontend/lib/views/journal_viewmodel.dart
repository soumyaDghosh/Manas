import 'package:collection/collection.dart';
import 'package:flutter/foundation.dart';

import '../models/session.dart';
import '../services/auth_service.dart';
import '../services/journal_service.dart';

class JournalViewModel extends ChangeNotifier {
  final AuthService _authService;
  final JournalService _journalService;

  bool _disposed = false;

  JournalViewModel({
    required AuthService authService,
    required JournalService journalService,
  }) : _authService = authService,
       _journalService = journalService;

  // --- STATE ---
  bool _isLoading = true;
  String? _errorMessage;
  Map<DateTime, List<Session>> _groupedSessions = {};

  // --- GETTERS ---
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  UnmodifiableMapView<DateTime, List<Session>> get groupedSessions =>
      UnmodifiableMapView(_groupedSessions);

  List<DateTime> get sortedDates =>
      _groupedSessions.keys.sorted((a, b) => b.compareTo(a));

  bool get hasEntries => _groupedSessions.isNotEmpty;
  int get totalSessionCount =>
      _groupedSessions.values.fold(0, (sum, list) => sum + list.length);

  // --- PUBLIC METHODS ---
  Future<void> fetchJournals() async {
    await _performAsyncOperation(() async {
      final token = await _getAuthToken();
      if (_disposed) return;

      final sessions = await _journalService.fetchSessions(token: token);
      if (_disposed) return;

      _processAndGroupSessions(sessions);
    });
  }

  Future<void> refresh() => fetchJournals();

  List<Session> getSessionsForDate(DateTime localDate) {
    final normalized = _normalizeDate(localDate);
    return _groupedSessions[normalized] ?? const [];
  }

  void clearData() {
    _groupedSessions.clear();
    _errorMessage = null;
    _isLoading = false;
    notifyListeners();
  }

  // --- PRIVATE METHODS ---
  Future<void> _performAsyncOperation(Future<void> Function() op) async {
    _setLoadingState(true);
    try {
      await op();
    } catch (e, st) {
      debugPrint('JournalViewModel error: $e\n$st');
      _setError(_mapErrorToMessage(e));
    } finally {
      _setLoadingState(false);
    }
  }

  Future<String> _getAuthToken() async {
    final token = await _authService.getIdToken();
    if (token == null) throw AuthException();
    return token;
  }

  void _processAndGroupSessions(List<Session> sessions) {
    _groupedSessions = groupBy(sessions, (Session s) {
      final local = s.createdAt;
      return DateTime(local.year, local.month, local.day);
    });

    for (final list in _groupedSessions.values) {
      list.sort(
        (a, b) => b.createdAt.toLocal().compareTo(a.createdAt.toLocal()),
      );
    }
  }

  DateTime _normalizeDate(DateTime dt) => DateTime(dt.year, dt.month, dt.day);

  void _setLoadingState(bool value) {
    _isLoading = value;
    if (value) _errorMessage = null;
    notifyListeners();
  }

  void _setError(String msg) {
    _errorMessage = msg;
    notifyListeners();
  }

  String _mapErrorToMessage(Object error) {
    if (error is AuthException) {
      return 'Please log in to view your journal entries.';
    } else if (error.toString().toLowerCase().contains('network')) {
      return 'Network error. Please check your connection.';
    }
    return 'Failed to load journal entries. Please try again later.';
  }

  // --- DISPOSE SAFE ---
  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }

  @override
  void notifyListeners() {
    if (!_disposed) {
      super.notifyListeners();
    }
  }
}

class AuthException implements Exception {}
