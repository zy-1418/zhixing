import 'package:flutter/material.dart';

import '../../widgets/placeholder_tab.dart';

class WriteNoteScreen extends StatelessWidget {
  const WriteNoteScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderTab(
      title: '写笔记',
      icon: Icons.edit_note_outlined,
      description: '文档、双联阅读与画布笔记将在此创建。',
    );
  }
}
