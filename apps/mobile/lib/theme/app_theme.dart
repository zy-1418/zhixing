import 'package:flutter/material.dart';

/// 知行 Demo 暖色美学：奶油米白背景 + 栗红强调色。
abstract final class AppColors {
  static const creamBackground = Color(0xFFF7F2EA);
  static const creamSurface = Color(0xFFFFFBF5);
  static const creamCard = Color(0xFFF0E8DC);
  static const maroon = Color(0xFF7A2E2A);
  static const maroonDark = Color(0xFF5C2220);
  static const textPrimary = Color(0xFF3D3832);
  static const textSecondary = Color(0xFF8A8278);
  static const divider = Color(0xFFE8DFD3);
  static const navInactive = Color(0xFF9C948A);
}

abstract final class AppTheme {
  static ThemeData get light {
    const seed = AppColors.maroon;
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seed,
      brightness: Brightness.light,
      surface: AppColors.creamSurface,
      primary: AppColors.maroon,
      onPrimary: Colors.white,
      onSurface: AppColors.textPrimary,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.creamBackground,
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.creamBackground,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        centerTitle: true,
      ),
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AppColors.maroon,
        foregroundColor: Colors.white,
        elevation: 4,
      ),
      bottomAppBarTheme: const BottomAppBarTheme(
        color: AppColors.creamSurface,
        elevation: 8,
        surfaceTintColor: Colors.transparent,
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
      ),
    );
  }
}
