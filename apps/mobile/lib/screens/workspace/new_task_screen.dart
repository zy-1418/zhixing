import 'dart:convert';

import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';

class NewTaskScreen extends StatefulWidget {
  const NewTaskScreen({super.key});

  @override
  State<NewTaskScreen> createState() => _NewTaskScreenState();
}

class _NewTaskScreenState extends State<NewTaskScreen> {
  static const _demoUserId = '00000000-0000-4000-8000-000000000001';

  final _api = ApiClient();
  final _instructionController = TextEditingController();
  final _contextController = TextEditingController();

  String _workflowType = 'research';
  String _priority = 'medium';
  bool _submitting = false;
  String? _result;

  @override
  void dispose() {
    _api.close();
    _instructionController.dispose();
    _contextController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final instruction = _instructionController.text.trim();
    if (instruction.isEmpty) {
      return;
    }
    setState(() {
      _submitting = true;
      _result = null;
    });

    try {
      final response = await _api.post(
        '/api/v1/tasks/sop',
        body: {
          'user_id': _demoUserId,
          'instruction': instruction,
          'workflow_type': _workflowType,
          'priority': _priority,
          'context_notes': _contextController.text.trim().isEmpty
              ? null
              : _contextController.text.trim(),
        },
      );
      final decoded = response.body.isEmpty
          ? {'status': response.statusCode}
          : jsonDecode(response.body);
      setState(
        () => _result = const JsonEncoder.withIndent('  ').convert(decoded),
      );
    } catch (error) {
      setState(() => _result = error.toString());
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('布置任务')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              '提交给 MetaGPT-X SOP',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Cloud 环境无法访问本机 MetaGPT-X，提交会展示后端占位或错误信息；本机启动 :8000 后可真实排队。',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _instructionController,
              minLines: 4,
              maxLines: 8,
              decoration: const InputDecoration(
                labelText: '任务说明',
                hintText: '例如：分析本周电池笔记，整理 3 个研究问题。',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _workflowType,
              decoration: const InputDecoration(
                labelText: '工作流类型',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'research', child: Text('研究型')),
                DropdownMenuItem(value: 'writing', child: Text('写作型')),
                DropdownMenuItem(value: 'search', child: Text('检索型')),
                DropdownMenuItem(value: 'custom', child: Text('自定义')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _workflowType = value);
                }
              },
            ),
            const SizedBox(height: 16),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'high', label: Text('高')),
                ButtonSegment(value: 'medium', label: Text('中')),
                ButtonSegment(value: 'low', label: Text('低')),
              ],
              selected: {_priority},
              onSelectionChanged: (values) {
                setState(() => _priority = values.first);
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _contextController,
              minLines: 3,
              maxLines: 6,
              decoration: const InputDecoration(
                labelText: '上下文笔记（可选）',
                hintText: '粘贴工作区笔记片段，后端会写入 MetaGPT spec。',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: _submitting ? null : _submit,
              icon: _submitting
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.rocket_launch_outlined),
              label: const Text('提交 SOP 任务'),
            ),
            if (_result != null) ...[
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
                  child: SelectableText(_result!),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
