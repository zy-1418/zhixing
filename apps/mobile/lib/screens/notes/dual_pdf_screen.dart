import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class DualPdfScreen extends StatelessWidget {
  const DualPdfScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('双联 PDF')),
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
                  Icon(
                    Icons.picture_as_pdf_outlined,
                    color: AppColors.maroon,
                    size: 48,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'pdf.js 双栏阅读占位',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                  ),
                  SizedBox(height: 12),
                  Text(
                    '静态页位于 apps/pdf_web/index.html。本机接入 WebView 后，左栏渲染 PDF，'
                    '右栏同步摘录和笔记 blocks。',
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
