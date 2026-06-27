import 'dart:convert';

import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';

class NewConversationScreen extends StatefulWidget {
  const NewConversationScreen({super.key});

  @override
  State<NewConversationScreen> createState() => _NewConversationScreenState();
}

class _NewConversationScreenState extends State<NewConversationScreen> {
  static const _demoUserId = '00000000-0000-4000-8000-000000000001';

  final _api = ApiClient();
  final _queryController = TextEditingController();
  final _noteIdController = TextEditingController();
  final _noteIds = <String>[];

  bool _submitting = false;
  String? _responseText;

  @override
  void dispose() {
    _api.close();
    _queryController.dispose();
    _noteIdController.dispose();
    super.dispose();
  }

  void _addNoteReference() {
    final value = _noteIdController.text.trim();
    if (value.isEmpty || _noteIds.contains(value)) {
      return;
    }
    setState(() {
      _noteIds.add(value);
      _noteIdController.clear();
    });
  }

  void _showPdfPlaceholder() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('PDF 导入入口已预留，文件上传走 Dify /upload 代理。')),
    );
  }

  Future<void> _send() async {
    final query = _queryController.text.trim();
    if (query.isEmpty) {
      return;
    }
    setState(() {
      _submitting = true;
      _responseText = null;
    });

    try {
      final response = await _api.post(
        '/api/v1/dify/chat',
        body: {
          'user_id': _demoUserId,
          'query': query,
          'note_ids': _noteIds,
        },
      );
      final decoded = const JsonEncoder.withIndent('  ').convert(
        jsonDecode(response.body),
      );
      setState(() => _responseText = decoded);
    } catch (error) {
      setState(() => _responseText = error.toString());
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('新对话')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              '和「林」对话',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '可引用笔记 ID 或预留 PDF 上传入口，后端会通过 Dify 代理处理上下文。',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _queryController,
              minLines: 5,
              maxLines: 10,
              decoration: const InputDecoration(
                labelText: '输入问题',
                hintText: '例如：总结我本周的电池材料笔记，列出 3 个研究问题。',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _noteIdController,
                    decoration: const InputDecoration(
                      labelText: '引用笔记 ID',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _addNoteReference(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filledTonal(
                  onPressed: _addNoteReference,
                  icon: const Icon(Icons.add_link),
                  tooltip: '添加引用',
                ),
              ],
            ),
            if (_noteIds.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _noteIds
                    .map(
                      (id) => InputChip(
                        label: Text('@$id'),
                        onDeleted: () => setState(() => _noteIds.remove(id)),
                      ),
                    )
                    .toList(),
              ),
            ],
            const SizedBox(height: 20),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: _showPdfPlaceholder,
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('导入 PDF'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _submitting ? null : _send,
                    icon: _submitting
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send_outlined),
                    label: const Text('发送'),
                  ),
                ),
              ],
            ),
            if (_responseText != null) ...[
              const SizedBox(height: 24),
              Card(
                color: AppColors.creamSurface,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                  side: const BorderSide(color: AppColors.divider),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: SelectableText(_responseText!),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
