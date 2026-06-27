import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class GraphWebViewScreen extends StatelessWidget {
  const GraphWebViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('知识图谱')),
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
            child: const Padding(
              padding: EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.hub_outlined, color: AppColors.maroon, size: 48),
                  SizedBox(height: 16),
                  Text(
                    'sigma.js WebView 占位',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                  ),
                  SizedBox(height: 12),
                  Text(
                    '静态页位于 apps/graph_web/index.html。本机接入 WebView 后可加载图谱，'
                    '并通过 /api/v1/graph/preview 或 Neo4j 数据渲染广场/DIY 图谱。',
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
