import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  static const _demoUserId = '00000000-0000-4000-8000-000000000001';

  final _api = ApiClient();
  late Future<Map<String, dynamic>> _profileFuture;

  @override
  void initState() {
    super.initState();
    _profileFuture = _load();
  }

  @override
  void dispose() {
    _api.close();
    super.dispose();
  }

  Future<Map<String, dynamic>> _load() {
    return _api.getJson('/api/v1/profile/$_demoUserId');
  }

  void _refresh() {
    setState(() {
      _profileFuture = _load();
    });
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: FutureBuilder<Map<String, dynamic>>(
          future: _profileFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.person_off_outlined,
                      size: 56,
                      color: AppColors.maroon,
                    ),
                    const SizedBox(height: 12),
                    Text('个人主页暂不可用：${snapshot.error}'),
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: _refresh,
                      icon: const Icon(Icons.refresh),
                      label: const Text('重试'),
                    ),
                  ],
                ),
              );
            }

            final profile = snapshot.data ?? const {};
            final stats = profile['stats'] as Map<String, dynamic>? ?? const {};
            final tags = profile['tags'] as List<dynamic>? ?? const [];
            final works = profile['works'] as List<dynamic>? ?? const [];

            return ListView(
              children: [
                Row(
                  children: [
                    const CircleAvatar(
                      radius: 32,
                      backgroundColor: AppColors.maroon,
                      child: Icon(Icons.person, color: Colors.white, size: 32),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            profile['display_name']?.toString() ?? '知行用户',
                            style: Theme.of(context)
                                .textTheme
                                .headlineSmall
                                ?.copyWith(fontWeight: FontWeight.w700),
                          ),
                          Text(
                            'Lv.${profile['level'] ?? 1} · ${profile['email'] ?? ''}',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                          ),
                        ],
                      ),
                    ),
                    IconButton.filledTonal(
                      onPressed: _refresh,
                      icon: const Icon(Icons.refresh),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    _StatCard(label: '作品', value: stats['notes'] ?? 0),
                    _StatCard(label: '帖子', value: stats['posts'] ?? 0),
                    _StatCard(label: '点赞', value: stats['liked'] ?? 0),
                    _StatCard(label: '收藏', value: stats['favorites'] ?? 0),
                  ],
                ),
                const SizedBox(height: 20),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: tags.isEmpty
                      ? [const Chip(label: Text('暂无标签'))]
                      : tags.map((tag) => Chip(label: Text('#$tag'))).toList(),
                ),
                const SizedBox(height: 24),
                Text(
                  '最近作品',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 12),
                ...works.map((item) {
                  final work = item as Map<String, dynamic>;
                  return Card(
                    color: AppColors.creamSurface,
                    elevation: 0,
                    child: ListTile(
                      leading: Icon(
                        work['type'] == 'note'
                            ? Icons.edit_note_outlined
                            : Icons.public_outlined,
                        color: AppColors.maroon,
                      ),
                      title: Text(work['title']?.toString() ?? '未命名'),
                      subtitle: Text(work['type']?.toString() ?? ''),
                    ),
                  );
                }),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({required this.label, required this.value});

  final String label;
  final Object value;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        color: AppColors.creamSurface,
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14),
          child: Column(
            children: [
              Text(
                value.toString(),
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: AppColors.maroon,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
