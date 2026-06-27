# 离线笔记缓存

## 已交付

- `apps/mobile/lib/services/offline_note_cache.dart`：最多保留 23 篇笔记草稿的缓存骨架。
- `WriteNoteScreen` 保存笔记时同步写入缓存。

## 当前限制

Cloud 环境缺少 Flutter SDK，且未引入本地持久化依赖。当前缓存为进程内骨架，用于约束容量和调用点。

## 后续持久化建议

1. 使用 `shared_preferences` 保存轻量 JSON 草稿，或使用 `sqlite`/`drift` 保存结构化 blocks。
2. 启动时加载最近 23 篇草稿。
3. API 恢复后执行后台同步，成功后移除 dirty 标记。
