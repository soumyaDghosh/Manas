enum MessageSender { user, bot }

class Message {
  final MessageSender sender;
  final String text;

  Message({required this.sender, required this.text});
}
