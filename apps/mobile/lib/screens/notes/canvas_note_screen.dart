import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class CanvasNoteScreen extends StatelessWidget {
  const CanvasNoteScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('无限画布')),
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
                  Icon(Icons.draw_outlined, color: AppColors.maroon, size: 48),
                  SizedBox(height: 16),
                  Text(
                    'tldraw WebView 占位',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                  ),
                  SizedBox(height: 12),
                  Text(
                    '静态页位于 apps/canvas_web/index.html。本机接入 WebView 后，'
                    'canvas 模板笔记可在这里编辑并回写 notes.blocks。',
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
