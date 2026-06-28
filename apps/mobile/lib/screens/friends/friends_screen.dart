import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class FriendsScreen extends StatelessWidget {
  const FriendsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          Text('好友', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
          SizedBox(height: 16),
          _FriendFeature(
            icon: Icons.people_outline,
            title: 'OpenIM 好友/群聊',
            description: 'docs/OPENIM.md 定义服务端桥接与 SDK 接入边界。',
          ),
          _FriendFeature(
            icon: Icons.psychology_outlined,
            title: '好友 AI 蒸馏',
            description: '按用户 Qdrant 分库，切换好友 AI 进行 RAG 对话。',
          ),
        ],
      ),
    );
  }
}

class _FriendFeature extends StatelessWidget {
  const _FriendFeature({
    required this.icon,
    required this.title,
    required this.description,
  });

  final IconData icon;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      child: ListTile(
        leading: Icon(icon, color: AppColors.maroon),
        title: Text(title),
        subtitle: Text(description),
      ),
    );
  }
}
