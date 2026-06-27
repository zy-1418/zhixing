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
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 16),
          const TextField(
            decoration: InputDecoration(
              prefixIcon: Icon(Icons.search),
              hintText: '搜索笔记、帖子、作者或话题',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          _FeedCard(
            title: '结构化辩论',
            subtitle: '赞/踩必须填写理由，优质观点会被置顶。',
            icon: Icons.balance_outlined,
          ),
          _FeedCard(
            title: '知识图谱',
            subtitle: 'sigma.js WebView 占位：apps/web/graph/index.html',
            icon: Icons.polyline_outlined,
          ),
          _FeedCard(
            title: '插件市场',
            subtitle: 'Dify tools 同步后展示可安装 Agent。',
            icon: Icons.storefront_outlined,
          ),
        ],
      ),
    );
  }
}

class _FeedCard extends StatelessWidget {
  const _FeedCard({
    required this.title,
    required this.subtitle,
    required this.icon,
  });

  final String title;
  final String subtitle;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      surfaceTintColor: Colors.transparent,
      child: ListTile(
        leading: Icon(icon, color: AppColors.maroon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
