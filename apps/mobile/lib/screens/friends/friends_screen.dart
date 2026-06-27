import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class FriendsScreen extends StatelessWidget {
  const FriendsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '好友',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 16),
          Card(
            color: AppColors.creamSurface,
            surfaceTintColor: Colors.transparent,
            child: const ListTile(
              leading: Icon(Icons.chat_outlined, color: AppColors.maroon),
              title: Text('OpenIM'),
              subtitle: Text('好友、群聊和团队空间 SDK 占位。'),
            ),
          ),
          Card(
            color: AppColors.creamSurface,
            surfaceTintColor: Colors.transparent,
            child: const ListTile(
              leading: Icon(Icons.smart_toy_outlined, color: AppColors.maroon),
              title: Text('好友 AI'),
              subtitle: Text('按用户 Qdrant 分库蒸馏好友 AI。'),
            ),
          ),
          Card(
            color: AppColors.creamSurface,
            surfaceTintColor: Colors.transparent,
            child: const ListTile(
              leading: Icon(Icons.apps_outlined, color: AppColors.maroon),
              title: Text('AI 小程序'),
              subtitle: Text('Dify Workflow + e2b 沙箱占位。'),
            ),
          ),
        ],
      ),
    );
  }
}
