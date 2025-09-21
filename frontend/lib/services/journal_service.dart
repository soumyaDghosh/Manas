import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/session.dart';

class JournalService {
  final String _apiUrl;

  JournalService()
    : _apiUrl = const String.fromEnvironment(
        'API_URL',
        defaultValue: 'https://manas-backend-production.up.railway.app',
      );

  Future<List<Session>> fetchSessions({required String token}) async {
    final response = await http.get(
      Uri.parse('$_apiUrl/api/v1/sessions'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> sessionList = data['sessions'];
      return sessionList.map((json) => Session.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load journal sessions.');
    }
  }
}
