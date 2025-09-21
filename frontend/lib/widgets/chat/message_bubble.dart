import 'package:flutter/material.dart';
import 'package:gpt_markdown/gpt_markdown.dart';
import '../../models/message.dart';

class MessageBubble extends StatefulWidget {
  final Message message;
  const MessageBubble({super.key, required this.message});

  @override
  State<MessageBubble> createState() => _MessageBubbleState();
}

class _MessageBubbleState extends State<MessageBubble>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<Offset> _offsetAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    )..forward();
    _offsetAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.5),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isUserMessage = widget.message.sender == MessageSender.user;

    return SlideTransition(
      position: _offsetAnimation,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6.0),
        child: Row(
          mainAxisAlignment: isUserMessage
              ? MainAxisAlignment.end
              : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (!isUserMessage) ...[
              const CircleAvatar(
                backgroundColor: Color(0xFF38005f),
                child: Icon(Icons.smart_toy_outlined, size: 20),
              ),
              const SizedBox(width: 8),
            ],

            Flexible(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  vertical: 12,
                  horizontal: 18,
                ),
                decoration: BoxDecoration(
                  color: isUserMessage
                      ? const Color(0xFF160842)
                      : const Color(0xFF38005f),
                  borderRadius: isUserMessage
                      ? const BorderRadius.only(
                          topLeft: Radius.circular(20),
                          topRight: Radius.circular(20),
                          bottomLeft: Radius.circular(20),
                        )
                      : const BorderRadius.only(
                          topLeft: Radius.circular(20),
                          topRight: Radius.circular(20),
                          bottomRight: Radius.circular(20),
                        ),
                ),
                child: GptMarkdown(
                  widget.message.text,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),

            if (isUserMessage) ...[
              const SizedBox(width: 8),
              const CircleAvatar(
                backgroundColor: Color(0xFF160842),
                child: Icon(Icons.person, size: 20),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
