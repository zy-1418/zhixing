# 桌面端打包

## 已交付

- `scripts/package-desktop.ps1`：Flutter desktop 打包入口。
- Tauri 路径预留：当前 Web 原型资源位于 `apps/*_web`，后续可封装成 Tauri shell。

## Cloud 限制

当前 Cloud 环境缺少 Flutter SDK，无法执行桌面端构建。请在本机安装 Flutter stable 后运行：

```powershell
powershell -File scripts/package-desktop.ps1 -Target flutter
```

## 后续建议

1. 按目标平台补齐 Flutter desktop runner。
2. 将 WebView 静态页打包为 Flutter assets。
3. 如选择 Tauri，新增 `apps/desktop`，复用 `apps/*_web` 静态页面和 API client。
