import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '个人',
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
              leading: CircleAvatar(
                backgroundColor: AppColors.maroon,
                child: Icon(Icons.person, color: Colors.white),
              ),
              title: Text('知行探索者'),
              subtitle: Text('作品 / 收藏 / 标签'),
            ),
          ),
          const _ProfileTile(
            icon: Icons.bookmarks_outlined,
            title: '作品与收藏',
            subtitle: '个人主页 API 占位。',
          ),
          const _ProfileTile(
            icon: Icons.account_balance_wallet_outlined,
            title: '钱包与订单',
            subtitle: 'Medusa 对接占位。',
          ),
          const _ProfileTile(
            icon: Icons.offline_pin_outlined,
            title: '离线缓存',
            subtitle: '最近 23 篇笔记优先缓存。',
          ),
          const _ProfileTile(
            icon: Icons.desktop_windows_outlined,
            title: '桌面端',
            subtitle: 'Flutter desktop / Tauri 打包脚本占位。',
          ),
        ],
      ),
    );
  }
}

class _ProfileTile extends StatelessWidget {
  const _ProfileTile({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  final IconData icon;
  final String title;
  final String subtitle;

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
