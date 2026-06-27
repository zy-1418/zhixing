# Flutter app — run `flutter create .` when SDK is available.
# Target: 五 Tab 导航（广场/工作区/写笔记/好友/个人）

## Init

```powershell
cd apps/mobile
flutter create . --org com.zhixing --project-name zhixing_mobile
```

## Phase 1 screens

- `lib/screens/square/` — 广场
- `lib/screens/workspace/` — 工作区树
- `lib/screens/notes/` — 写笔记
- `lib/screens/friends/` — 好友
- `lib/screens/profile/` — 个人
- `lib/services/api_client.dart` — 知行 API :8080
