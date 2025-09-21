extension TitleCaseExtension on String {
  /// Converts a string to title case.
  String toTitleCase() {
    if (isEmpty) {
      return '';
    }
    final List<String> words = trim().split(RegExp(r'\s+'));

    final capitalizedWords = words.map((word) {
      if (word.isEmpty) {
        return '';
      }
      final String firstLetter = word.substring(0, 1).toUpperCase();
      final String remainingLetters = word.substring(1).toLowerCase();
      return '$firstLetter$remainingLetters';
    });

    return capitalizedWords.join(' ');
  }
}
