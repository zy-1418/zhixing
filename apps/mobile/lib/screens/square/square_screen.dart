import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class SquareScreen extends StatelessWidget {
  const SquareScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '广场',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 16),
          SearchBar(
            hintText: '搜索笔记、帖子、作者或话题',
            leading: const Icon(Icons.search),
            onSubmitted: (_) {},
          ),
          const SizedBox(height: 16),
          const _FeedCard(
            title: '结构化辩论',
            body: '赞/踩必须填写理由，正反评论会按证据完整度置顶。',
            icon: Icons.forum_outlined,
          ),
          const _FeedCard(
            title: '知识图谱',
            body: 'Phase 3 将通过 sigma.js WebView 展示论点演化。',
            icon: Icons.hub_outlined,
          ),
        ],
      ),
    );
  }
}

class _FeedCard extends StatelessWidget {
  const _FeedCard({
    required this.title,
    required this.body,
    required this.icon,
  });

  final String title;
  final String body;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      child: ListTile(
        leading: Icon(icon, color: AppColors.maroon),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(body),
      ),
    );
  }
}
