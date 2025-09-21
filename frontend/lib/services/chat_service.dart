import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  final String _apiUrl;

  ChatService()
    : _apiUrl = const String.fromEnvironment(
        'API_URL',
        defaultValue: 'https://manas-backend-production.up.railway.app',
      );

  Future<String> processMessage({
    required String text,
    required String token,
  }) async {
    final response = await http.post(
      Uri.parse('$_apiUrl/api/v1/process'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'text': text,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );

    if (response.statusCode == 202) {
      return jsonDecode(response.body)['reply'] ?? 'No reply found.';
    } else {
      throw Exception('Failed to get reply from server.');
    }
  }

  Future<void> endSession({required String token}) async {
    try {
      await http.post(
        Uri.parse('$_apiUrl/api/v1/end-session'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );
    } catch (e) {
      print("Could not notify server of session end: $e");
    }
  }
}
