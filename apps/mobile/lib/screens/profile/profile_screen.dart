import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          CircleAvatar(
            radius: 36,
            backgroundColor: AppColors.maroon,
            child: Text('行', style: TextStyle(color: Colors.white, fontSize: 28)),
          ),
          SizedBox(height: 12),
          Center(
            child: Text('知行用户', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
          ),
          SizedBox(height: 20),
          _ProfileTile(title: '作品', icon: Icons.work_outline),
          _ProfileTile(title: '收藏', icon: Icons.bookmark_border),
          _ProfileTile(title: '标签', icon: Icons.local_offer_outlined),
          _ProfileTile(title: '离线缓存 23 篇笔记', icon: Icons.offline_pin_outlined),
          _ProfileTile(title: '桌面端打包状态', icon: Icons.desktop_windows_outlined),
        ],
      ),
    );
  }
}

class _ProfileTile extends StatelessWidget {
  const _ProfileTile({required this.title, required this.icon});

  final String title;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      child: ListTile(
        leading: Icon(icon, color: AppColors.maroon),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
