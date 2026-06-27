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
  final _taskController = TextEditingController();
  final _noteController = TextEditingController();
  String _apiStatus = '未连接';
  String _taskStatus = '尚未提交任务';

  @override
  void initState() {
    super.initState();
    _refreshHealth();
  }

  @override
  void dispose() {
    _api.close();
    _taskController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _refreshHealth() async {
    try {
      final health = await _api.getJson('/health');
      if (!mounted) return;
      setState(() => _apiStatus = 'API ${health['status']}');
    } catch (error) {
      if (!mounted) return;
      setState(() => _apiStatus = 'API 未连接：$error');
    }
  }

  Future<void> _submitTask() async {
    final instruction = _taskController.text.trim();
    if (instruction.isEmpty) {
      setState(() => _taskStatus = '请输入任务描述');
      return;
    }
    setState(() => _taskStatus = '提交中...');
    try {
      final response = await _api.postJson(
        '/api/v1/tasks/sop',
        body: {
          'instruction': instruction,
          'workflow_type': 'research',
          'priority': 'medium',
          'context_notes': _noteController.text.trim(),
          'skip_dev': false,
        },
      );
      if (!mounted) return;
      setState(() {
        _taskStatus = '已提交：${response['metagpt_job_id']}';
      });
    } catch (error) {
      if (!mounted) return;
      setState(() => _taskStatus = '提交失败：$error');
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
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
              FilledButton.tonalIcon(
                onPressed: _refreshHealth,
                icon: const Icon(Icons.sync),
                label: const Text('刷新'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(_apiStatus, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 20),
          _SectionCard(
            title: '文件树',
            icon: Icons.account_tree_outlined,
            child: Column(
              children: const [
                _FolderTile(title: '作品集', children: ['任务复盘', '导出文档']),
                _FolderTile(title: '工作流', children: ['研究型 SOP', '写作型 SOP']),
                _FolderTile(title: '对话', children: ['林 · 新对话']),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _SectionCard(
            title: '新对话',
            icon: Icons.chat_bubble_outline,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: _noteController,
                  minLines: 3,
                  maxLines: 6,
                  decoration: const InputDecoration(
                    labelText: '导入 PDF / @引用笔记后的上下文',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: [
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
              ],
            ),
          ),
          const SizedBox(height: 16),
          _SectionCard(
            title: '布置任务',
            icon: Icons.task_alt_outlined,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: _taskController,
                  decoration: const InputDecoration(
                    labelText: '研究 / 写作 / 检索任务',
                    hintText: '例如：整理本周电池笔记并生成研究问题',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: _submitTask,
                  icon: const Icon(Icons.send_outlined),
                  label: const Text('提交 SOP'),
                ),
                const SizedBox(height: 8),
                Text(_taskStatus),
              ],
            ),
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
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
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

class _FolderTile extends StatelessWidget {
  const _FolderTile({required this.title, required this.children});

  final String title;
  final List<String> children;

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      tilePadding: EdgeInsets.zero,
      leading: const Icon(Icons.folder_outlined),
      title: Text(title),
      children: children
          .map(
            (item) => ListTile(
              dense: true,
              leading: const Icon(Icons.insert_drive_file_outlined, size: 18),
              title: Text(item),
            ),
          )
          .toList(),
    );
  }
}
