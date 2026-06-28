import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';

class WorkspaceScreen extends StatefulWidget {
  const WorkspaceScreen({super.key});

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  final _api = ApiClient();
  late final Future<Map<String, dynamic>> _health = _api.getJson('/health');

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '工作区',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 12),
          FutureBuilder<Map<String, dynamic>>(
            future: _health,
            builder: (context, snapshot) {
              final ok = snapshot.hasData;
              return _StatusCard(
                title: ok ? 'API 已连接' : 'API 待连接',
                subtitle: ok
                    ? 'MetaGPT: ${snapshot.data?['metagpt_x_api']}'
                    : '启动 services/api 后会显示工作区树与任务状态。',
                icon: ok ? Icons.check_circle_outline : Icons.cloud_off_outlined,
              );
            },
          ),
          const SizedBox(height: 16),
          const _SectionCard(
            title: '文件树',
            description: '作品集 / 小程序 / 工作流 / skills / 对话',
            icon: Icons.account_tree_outlined,
          ),
          const _SectionCard(
            title: '新对话',
            description: '支持导入 PDF、@引用笔记并经 Dify 代理到「林」Agent。',
            icon: Icons.chat_bubble_outline,
          ),
          const _SectionCard(
            title: '布置任务',
            description: '研究型 / 写作型 / 检索型任务会进入 MetaGPT SOP 队列。',
            icon: Icons.task_alt_outlined,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _api.close();
    super.dispose();
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({
    required this.title,
    required this.subtitle,
    required this.icon,
  });

  final String title;
  final String subtitle;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return _SectionCard(title: title, description: subtitle, icon: icon);
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.title,
    required this.description,
    required this.icon,
  });

  final String title;
  final String description;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(icon, color: AppColors.maroon),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(description),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
