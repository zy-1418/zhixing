import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';
import 'new_conversation_screen.dart';
import 'new_task_screen.dart';

class WorkspaceScreen extends StatefulWidget {
  const WorkspaceScreen({super.key});

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  static const _demoUserId = '00000000-0000-4000-8000-000000000001';

  final _api = ApiClient();
  late Future<List<WorkspaceFolderNode>> _foldersFuture;

  @override
  void initState() {
    super.initState();
    _foldersFuture = _loadFolders();
  }

  @override
  void dispose() {
    _api.close();
    super.dispose();
  }

  Future<List<WorkspaceFolderNode>> _loadFolders() async {
    final items = await _api.getJsonList(
      '/api/v1/workspace/folders/tree',
      queryParameters: {'user_id': _demoUserId},
    );
    return items
        .cast<Map<String, dynamic>>()
        .map(WorkspaceFolderNode.fromJson)
        .toList();
  }

  void _refresh() {
    setState(() {
      _foldersFuture = _loadFolders();
    });
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    '工作区',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          color: AppColors.textPrimary,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
                IconButton.filledTonal(
                  onPressed: _refresh,
                  icon: const Icon(Icons.refresh),
                  tooltip: '刷新工作区',
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '同步 /api/v1/workspace/folders/tree，展示作品集、小程序、工作流与对话分区。',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const NewConversationScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add_comment_outlined),
                    label: const Text('新对话'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const NewTaskScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add_task),
                    label: const Text('布置任务'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: FutureBuilder<List<WorkspaceFolderNode>>(
                future: _foldersFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return _WorkspaceMessage(
                      icon: Icons.cloud_off_outlined,
                      title: '暂时无法连接知行 API',
                      description: '${snapshot.error}\n\n请确认 services/api 已在 :8080 启动。',
                      action: FilledButton.icon(
                        onPressed: _refresh,
                        icon: const Icon(Icons.refresh),
                        label: const Text('重试'),
                      ),
                    );
                  }
                  final folders = snapshot.data ?? const [];
                  if (folders.isEmpty) {
                    return _WorkspaceMessage(
                      icon: Icons.create_new_folder_outlined,
                      title: '还没有工作区文件夹',
                      description: '创建作品集、工作流或对话分区后，会在这里显示树形结构。',
                      action: OutlinedButton.icon(
                        onPressed: _refresh,
                        icon: const Icon(Icons.refresh),
                        label: const Text('刷新'),
                      ),
                    );
                  }
                  return ListView.separated(
                    itemCount: folders.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      return _FolderTile(node: folders[index]);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class WorkspaceFolderNode {
  const WorkspaceFolderNode({
    required this.id,
    required this.name,
    required this.folderType,
    required this.children,
  });

  final String id;
  final String name;
  final String folderType;
  final List<WorkspaceFolderNode> children;

  factory WorkspaceFolderNode.fromJson(Map<String, dynamic> json) {
    final childrenJson = (json['children'] as List<dynamic>? ?? const []);
    return WorkspaceFolderNode(
      id: json['id'] as String,
      name: json['name'] as String? ?? '未命名',
      folderType: json['folder_type'] as String? ?? 'portfolio',
      children: childrenJson
          .cast<Map<String, dynamic>>()
          .map(WorkspaceFolderNode.fromJson)
          .toList(),
    );
  }
}

class _FolderTile extends StatelessWidget {
  const _FolderTile({required this.node, this.depth = 0});

  final WorkspaceFolderNode node;
  final int depth;

  @override
  Widget build(BuildContext context) {
    final leading = switch (node.folderType) {
      'miniapp' => Icons.apps_outlined,
      'workflow' => Icons.account_tree_outlined,
      'skills' => Icons.psychology_outlined,
      'conversation' => Icons.chat_bubble_outline,
      _ => Icons.folder_outlined,
    };

    return Card(
      color: AppColors.creamSurface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: AppColors.divider),
      ),
      child: ExpansionTile(
        initiallyExpanded: depth == 0,
        leading: Icon(leading, color: AppColors.maroon),
        title: Text(
          node.name,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text('${node.folderType} · ${node.children.length} 个子项'),
        childrenPadding: EdgeInsets.only(left: 16.0 + depth * 8, right: 8),
        children: node.children
            .map((child) => _FolderTile(node: child, depth: depth + 1))
            .toList(),
      ),
    );
  }
}

class _WorkspaceMessage extends StatelessWidget {
  const _WorkspaceMessage({
    required this.icon,
    required this.title,
    required this.description,
    required this.action,
  });

  final IconData icon;
  final String title;
  final String description;
  final Widget action;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        color: AppColors.creamSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.divider),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 56, color: AppColors.maroon),
              const SizedBox(height: 16),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              action,
            ],
          ),
        ),
      ),
    );
  }
}
