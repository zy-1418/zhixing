import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class WriteNoteScreen extends StatefulWidget {
  const WriteNoteScreen({super.key});

  @override
  State<WriteNoteScreen> createState() => _WriteNoteScreenState();
}

class _WriteNoteScreenState extends State<WriteNoteScreen> {
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();
  String _template = 'document';

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            '写笔记',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(
              labelText: '标题',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: [
              for (final item in const ['document', 'dual', 'canvas', 'mindmap'])
                ChoiceChip(
                  label: Text(item),
                  selected: _template == item,
                  onSelected: (_) => setState(() => _template = item),
                ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _bodyController,
            minLines: 12,
            maxLines: 24,
            decoration: const InputDecoration(
              alignLabelWithHint: true,
              labelText: '正文',
              hintText: '记录想法、摘录或任务上下文...',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('保存草稿'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.cloud_upload_outlined),
                  label: const Text('同步笔记'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Card(
            color: AppColors.creamSurface,
            surfaceTintColor: Colors.transparent,
            child: ListTile(
              leading: const Icon(Icons.auto_awesome_outlined, color: AppColors.maroon),
              title: const Text('模板说明'),
              subtitle: Text(
                _template == 'document'
                    ? '纯文档模板直接映射 notes.blocks。'
                    : '$_template 模板将在 WebView 能力可用后替换为专用编辑器。',
              ),
            ),
          ),
        ],
      ),
    );
  }
}
