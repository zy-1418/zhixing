import 'package:flutter/material.dart';

import '../../services/api_client.dart';
import '../../theme/app_theme.dart';
import 'graph_webview_screen.dart';

class SquareScreen extends StatefulWidget {
  const SquareScreen({super.key});

  @override
  State<SquareScreen> createState() => _SquareScreenState();
}

class _SquareScreenState extends State<SquareScreen> {
  final _api = ApiClient();
  final _controller = TextEditingController();

  bool _loading = false;
  List<dynamic> _hits = const [];
  String? _message;

  @override
  void dispose() {
    _api.close();
    _controller.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = _controller.text.trim();
    if (query.isEmpty) {
      return;
    }
    setState(() {
      _loading = true;
      _message = null;
      _hits = const [];
    });

    try {
      final result = await _api.getJson(
        '/api/v1/search',
        queryParameters: {'q': query, 'type': 'all'},
      );
      setState(() {
        _hits = (result['hits'] as List<dynamic>? ?? const []);
        _message = '来源：${result['mode'] ?? 'unknown'}';
      });
    } catch (error) {
      setState(() => _message = error.toString());
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '广场',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '搜索笔记与帖子；后端优先使用 Meilisearch，不可用时回退数据库查询。',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const GraphWebViewScreen()),
                );
              },
              icon: const Icon(Icons.hub_outlined),
              label: const Text('打开知识图谱'),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: '搜索',
                hintText: '输入关键词',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  onPressed: _loading ? null : _search,
                  icon: const Icon(Icons.search),
                ),
              ),
              onSubmitted: (_) => _search(),
            ),
            if (_message != null) ...[
              const SizedBox(height: 12),
              Text(
                _message!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
            ],
            const SizedBox(height: 16),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _hits.isEmpty
                      ? const Center(child: Text('输入关键词搜索广场内容'))
                      : ListView.separated(
                          itemCount: _hits.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, index) {
                            final item = _hits[index] as Map<String, dynamic>;
                            return Card(
                              color: AppColors.creamSurface,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(18),
                                side: const BorderSide(color: AppColors.divider),
                              ),
                              child: ListTile(
                                leading: Icon(
                                  item['type'] == 'note'
                                      ? Icons.edit_note_outlined
                                      : Icons.public_outlined,
                                  color: AppColors.maroon,
                                ),
                                title: Text(item['title']?.toString() ?? '未命名'),
                                subtitle: Text(
                                  item['summary']?.toString() ?? item.toString(),
                                ),
                              ),
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
