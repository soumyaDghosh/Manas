import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/auth_service.dart';
import '../../services/chat_service.dart';
import '../../views/chat_viewmodel.dart';
import '../../widgets/chat/loading_message_bubble.dart';
import '../../widgets/chat/message_bubble.dart';
import '../../widgets/chat/start_view.dart';
import '../../widgets/chat/text_composer.dart';

class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ChatViewModel(
        authService: context.read<AuthService>(),
        chatService: ChatService(),
      ),
      child: const _ChatView(),
    );
  }
}

class _ChatView extends StatefulWidget {
  const _ChatView();

  @override
  State<_ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<_ChatView>
    with AutomaticKeepAliveClientMixin {
  final ScrollController _scrollController = ScrollController();
  late final ChatViewModel _viewModel;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _viewModel = context.read<ChatViewModel>();
    _viewModel.addListener(_scrollToBottomOnUpdate);
  }

  @override
  void dispose() {
    _viewModel.removeListener(_scrollToBottomOnUpdate);
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottomOnUpdate() {
    if (!mounted) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final viewModel = context.watch<ChatViewModel>();

    return PopScope(
      canPop: !viewModel.isSessionActive,
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) return;
        if (viewModel.isSessionActive) {
          viewModel.endSession();
        }
      },
      child: Scaffold(
        body: viewModel.isSessionActive
            ? _ChatInterface(
                viewModel: viewModel,
                controller: _scrollController,
              )
            : StartView(onStartSession: viewModel.startSession),
      ),
    );
  }
}

class _ChatInterface extends StatelessWidget {
  final ChatViewModel viewModel;
  final ScrollController controller;

  const _ChatInterface({required this.viewModel, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            controller: controller,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
            itemCount: viewModel.chat.length + (viewModel.isLoading ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == viewModel.chat.length) {
                return const LoadingMessageBubble();
              }
              return MessageBubble(message: viewModel.chat[index]);
            },
          ),
        ),
        const Divider(height: 1),
        TextComposer(
          isLoading: viewModel.isLoading,
          onSendMessage: viewModel.sendMessage,
          onEndSession: viewModel.endSession,
        ),
      ],
    );
  }
}
