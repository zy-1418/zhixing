# 双联 PDF 阅读

## 已交付

- `apps/pdf_web/index.html`：pdf.js 双栏阅读静态原型。
- `apps/mobile/lib/screens/notes/dual_pdf_screen.dart`：Flutter WebView 占位入口。

## 设计

- 左栏渲染 PDF 原文。
- 右栏展示摘录、批注和知行 document blocks。
- 后续接入 pdf.js 文本选择事件，将选中文本写入 `notes.blocks`。

Cloud 环境缺少 Flutter SDK，因此当前不引入 WebView 插件；本机接入方式同 `docs/WORKFLOW_UI.md`。
