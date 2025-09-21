class Session {
  final String mood;
  final String summary;
  final DateTime createdAt;

  Session({required this.mood, required this.summary, required this.createdAt});

  factory Session.fromJson(Map<String, dynamic> json) {
    return Session(
      mood: json['mood'] as String,
      summary: json['summary'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
