import 'package:flutter/material.dart';

class TextComposer extends StatefulWidget {
  final bool isLoading;
  final Function(String) onSendMessage;
  final VoidCallback onEndSession;

  const TextComposer({
    super.key,
    required this.onSendMessage,
    required this.onEndSession,
    this.isLoading = false,
  });

  @override
  State<TextComposer> createState() => _TextComposerState();
}

class _TextComposerState extends State<TextComposer> {
  final TextEditingController _textController = TextEditingController();
  bool _showSendButton = false;

  @override
  void initState() {
    super.initState();
    _textController.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    setState(() {
      _showSendButton = _textController.text.trim().isNotEmpty;
    });
  }

  void _handleSend() {
    if (_textController.text.trim().isEmpty) return;
    widget.onSendMessage(_textController.text);
    _textController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
      color: Colors.white,
      child: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(30.0),
                ),
                child: TextField(
                  controller: _textController,
                  onSubmitted: (_) => _handleSend(),
                  keyboardType: TextInputType.multiline,
                  maxLines: null,
                  decoration: const InputDecoration(
                    hintText: "Type a message...",
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(
                      horizontal: 20.0,
                      vertical: 14.0,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),

            CircleAvatar(
              backgroundColor: Colors.red.shade400,
              child: IconButton(
                icon: const Icon(Icons.stop, color: Colors.white),
                tooltip: 'End Session',
                onPressed: widget.onEndSession,
              ),
            ),

            const SizedBox(width: 4),

            AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              transitionBuilder: (child, animation) =>
                  ScaleTransition(scale: animation, child: child),
              child: _showSendButton
                  ? CircleAvatar(
                      backgroundColor: const Color(0xFF38005f),
                      child: IconButton(
                        icon: const Icon(Icons.send, color: Colors.white),
                        onPressed: widget.isLoading ? null : _handleSend,
                      ),
                    )
                  : const SizedBox(width: 0),
            ),
          ],
        ),
      ),
    );
  }
}
