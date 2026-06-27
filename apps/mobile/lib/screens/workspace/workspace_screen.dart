import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class WorkspaceScreen extends StatefulWidget {
  const WorkspaceScreen({super.key});

  @override
  State<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends State<WorkspaceScreen> {
  final _taskController = TextEditingController();
  String _workflowType = 'research';

  @override
  void dispose() {
    _taskController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '工作区',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 16),
          _SectionCard(
            title: '文件树',
            icon: Icons.account_tree_outlined,
            child: Column(
              children: const [
                _TreeTile(label: '作品集', icon: Icons.folder_outlined, depth: 0),
                _TreeTile(label: '对话', icon: Icons.chat_bubble_outline, depth: 1),
                _TreeTile(label: '任务复盘', icon: Icons.task_alt_outlined, depth: 1),
                _TreeTile(label: 'skills', icon: Icons.extension_outlined, depth: 0),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _SectionCard(
            title: '新对话',
            icon: Icons.forum_outlined,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.add_comment_outlined),
                  label: const Text('创建对话'),
                ),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('导入 PDF'),
                ),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.note_add_outlined),
                  label: const Text('@引用笔记'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _SectionCard(
            title: '布置任务',
            icon: Icons.rocket_launch_outlined,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: _taskController,
                  minLines: 2,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    hintText: '例如：分析本周电池笔记并整理 3 个研究问题',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: [
                    for (final item in const ['research', 'writing', 'search', 'custom'])
                      ChoiceChip(
                        label: Text(item),
                        selected: _workflowType == item,
                        onSelected: (_) => setState(() => _workflowType = item),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.send_outlined),
                  label: const Text('提交 SOP 任务'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _SectionCard(
            title: '工作流编辑器',
            icon: Icons.hub_outlined,
            child: const Text('React Flow WebView 占位：apps/web/workflow/index.html'),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.title,
    required this.icon,
    required this.child,
  });

  final String title;
  final IconData icon;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.creamSurface,
      surfaceTintColor: Colors.transparent,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: AppColors.maroon),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

class _TreeTile extends StatelessWidget {
  const _TreeTile({
    required this.label,
    required this.icon,
    required this.depth,
  });

  final String label;
  final IconData icon;
  final int depth;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(left: depth * 20, top: 6, bottom: 6),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.textSecondary),
          const SizedBox(width: 8),
          Text(label),
        ],
      ),
    );
  }
}
