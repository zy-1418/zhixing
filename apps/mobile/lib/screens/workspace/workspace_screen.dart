import 'package:flutter/material.dart';

import '../../widgets/placeholder_tab.dart';

class WorkspaceScreen extends StatelessWidget {
  const WorkspaceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderTab(
      title: '工作区',
      icon: Icons.folder_outlined,
      description: '文件树、任务与 AI 工作流将在此管理。',
    );
  }
}
