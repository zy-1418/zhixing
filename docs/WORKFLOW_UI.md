# 工作流编辑器 UI

## 已交付

- `apps/workflow_web/index.html`：React Flow 静态原型，展示 Dify/MetaGPT-X 到工作区产物的任务编排。
- `apps/mobile/lib/screens/workspace/workflow_webview_screen.dart`：Flutter 工作区入口占位。

## Cloud 限制

当前 Cloud 环境缺少 Flutter SDK，无法通过 `flutter pub add webview_flutter` 或 `flutter run` 验证 WebView 插件。因此移动端先交付占位入口，避免引入未解析依赖。

## 本机接入建议

1. 在 `apps/mobile` 中添加 WebView 插件：

   ```bash
   flutter pub add webview_flutter
   ```

2. 将 `apps/workflow_web/index.html` 作为 asset 或通过本地静态服务暴露。
3. 在 `WorkflowWebViewScreen` 中使用 `WebViewWidget` 加载页面。
4. 通过 JavaScript channel 把节点编辑结果回传到知行 API。
