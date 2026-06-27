# tldraw 无限画布

## 已交付

- `apps/canvas_web/index.html`：tldraw 静态画布原型。
- `apps/mobile/lib/screens/notes/canvas_note_screen.dart`：Flutter WebView 占位入口。
- `notes.template_type` 已支持 `canvas`。

## 本机接入

Cloud 环境缺少 Flutter SDK，当前未引入 WebView 插件。本机可按 `docs/WORKFLOW_UI.md` 的方式接入 `webview_flutter`，加载 `apps/canvas_web/index.html`，并通过 JavaScript channel 将 tldraw document JSON 写回 `notes.blocks`。
