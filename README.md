# 知行（Zhixing）— AI 原生社交知识平台
#
# 复刻「知行 v0.5」Demo，嵌入 MetaGPT-X 代码工厂。
# 文档：docs/PLAN.md | docs/STACK.md | docs/ARCHITECTURE.md

## 快速开始

```powershell
# 1. 拉 vendor
powershell -File scripts/clone-deps.ps1

# 2. 中间件
cd infra && docker compose up -d

# 3. MetaGPT-X（需已配置 LLM）
powershell -File G:\MetaGPT\scripts\start_metagpt_x_api.ps1

# 4. 知行 API
cd services\api
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8080

# 5. Flutter
cd apps\mobile && flutter run
```

## Cursor 自动续跑

项目已配置 `.cursor/hooks.json`：Agent 完成一步后会读取 `WORKFLOW_STATE.json` 自动执行下一步，无需反复输入「继续」。

关闭自动续跑：将 `.cursor/WORKFLOW_STATE.json` 中 `auto_continue` 设为 `false`。

## 目录

```
apps/mobile/           Flutter 客户端
services/api/          知行 FastAPI 网关
services/metagpt-bridge/  MetaGPT-X 客户端
infra/                 Docker Compose
vendor/                第三方开源（dify 等）
docs/                  方案与架构
```
