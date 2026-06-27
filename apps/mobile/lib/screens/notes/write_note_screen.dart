import 'dart:convert';

import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';

class WriteNoteScreen extends StatefulWidget {
  const WriteNoteScreen({super.key});

  @override
  State<WriteNoteScreen> createState() => _WriteNoteScreenState();
}

class _WriteNoteScreenState extends State<WriteNoteScreen> {
  static const _demoUserId = '00000000-0000-4000-8000-000000000001';

  final _api = ApiClient();
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();

  bool _saving = false;
  String? _message;

  @override
  void dispose() {
    _api.close();
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  List<Map<String, dynamic>> _blocks() {
    final paragraphs = _bodyController.text
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList();
    return [
      {'type': 'heading', 'level': 1, 'text': _titleController.text.trim()},
      ...paragraphs.map((text) => {'type': 'paragraph', 'text': text}),
    ];
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _message = null;
    });

    try {
      final response = await _api.post(
        '/api/v1/notes',
        body: {
          'user_id': _demoUserId,
          'title': _titleController.text.trim(),
          'template_type': 'document',
          'blocks': _blocks(),
        },
      );
      final decoded = response.body.isEmpty
          ? {'status': response.statusCode}
          : jsonDecode(response.body);
      setState(
        () => _message = const JsonEncoder.withIndent('  ').convert(decoded),
      );
    } catch (error) {
      setState(() => _message = error.toString());
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
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
          const SizedBox(height: 8),
          Text(
            '纯文档模板会保存为 heading + paragraph blocks，后续可扩展为双联阅读和画布。',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _titleController,
            textInputAction: TextInputAction.next,
            decoration: const InputDecoration(
              labelText: '标题',
              hintText: '给这篇笔记起个名字',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _bodyController,
            minLines: 12,
            maxLines: 24,
            decoration: const InputDecoration(
              labelText: '正文',
              hintText: '每个非空行会保存为一个 paragraph block。',
              alignLabelWithHint: true,
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: _saving ? null : _save,
            icon: _saving
                ? const SizedBox.square(
                    dimension: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.save_outlined),
            label: const Text('保存笔记'),
          ),
          if (_message != null) ...[
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
                child: SelectableText(_message!),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
