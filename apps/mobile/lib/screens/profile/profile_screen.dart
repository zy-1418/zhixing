import 'package:flutter/material.dart';

import '../../widgets/placeholder_tab.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderTab(
      title: '个人',
      icon: Icons.person_outline,
      description: '个人资料、等级与设置将在此管理。',
    );
  }
}
