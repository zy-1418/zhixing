import 'package:flutter/material.dart';

import '../../widgets/placeholder_tab.dart';

class FriendsScreen extends StatelessWidget {
  const FriendsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderTab(
      title: '好友',
      icon: Icons.people_outline,
      description: '好友列表与群聊将在此展示。',
    );
  }
}
