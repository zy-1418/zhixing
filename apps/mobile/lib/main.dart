import 'package:flutter/material.dart';

import 'screens/friends/friends_screen.dart';
import 'screens/notes/write_note_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/square/square_screen.dart';
import 'screens/workspace/workspace_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const ZhixingApp());
}

class ZhixingApp extends StatelessWidget {
  const ZhixingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '知行',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  static const _writeNoteIndex = 2;

  int _currentIndex = 0;

  final _screens = const [
    SquareScreen(),
    WorkspaceScreen(),
    WriteNoteScreen(),
    FriendsScreen(),
    ProfileScreen(),
  ];

  static const _tabLabels = ['广场', '工作区', '写笔记', '好友', '个人'];
  static const _tabIcons = [
    Icons.public_outlined,
    Icons.folder_outlined,
    Icons.edit_note_outlined,
    Icons.people_outline,
    Icons.person_outline,
  ];
  static const _tabActiveIcons = [
    Icons.public,
    Icons.folder,
    Icons.edit_note,
    Icons.people,
    Icons.person,
  ];

  void _onTabSelected(int index) {
    setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _onTabSelected(_writeNoteIndex),
        tooltip: '写笔记',
        elevation: _currentIndex == _writeNoteIndex ? 6 : 4,
        child: const Icon(Icons.edit_note, size: 28),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        height: 64,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        shape: const CircularNotchedRectangle(),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: List.generate(_tabLabels.length, (index) {
            if (index == _writeNoteIndex) {
              return const SizedBox(width: 56);
            }
            return _NavItem(
              label: _tabLabels[index],
              icon: _tabIcons[index],
              activeIcon: _tabActiveIcons[index],
              selected: _currentIndex == index,
              onTap: () => _onTabSelected(index),
            );
          }),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.label,
    required this.icon,
    required this.activeIcon,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final IconData activeIcon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = selected ? AppColors.maroon : AppColors.navInactive;

    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(selected ? activeIcon : icon, color: color, size: 24),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  color: color,
                  fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
