import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class WorkflowWebViewScreen extends StatelessWidget {
  const WorkflowWebViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('工作流编辑器')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
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
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(
                    Icons.account_tree_outlined,
                    color: AppColors.maroon,
                    size: 48,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'React Flow WebView 占位',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '静态页位于 apps/workflow_web/index.html。Cloud 环境没有 Flutter SDK，'
                    '本机可接入 webview_flutter 后加载该静态页或本地 dev server。',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.textSecondary,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
