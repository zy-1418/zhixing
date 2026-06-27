import 'package:flutter/material.dart';

import '../../widgets/placeholder_tab.dart';

class SquareScreen extends StatelessWidget {
  const SquareScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderTab(
      title: '广场',
      icon: Icons.public_outlined,
      description: '热搜、辩论与社区动态将在此展示。',
    );
  }
}
