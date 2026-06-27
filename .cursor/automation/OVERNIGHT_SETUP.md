# 知行 — 夜间全量 Cloud Agent 自动化

> 目标：从当前 P0 一直跑到 P4 完成，或直到你早上查看。  
> **当前 IDE 会话无法直接打开 Automations 编辑器**，请按下方「一键启动」操作。

---

## 自动化草案（在 Automations 编辑器中创建）

| 字段 | 内容 |
|------|------|
| **名称** | 知行全量夜间实施 |
| **描述** | 按 WORKFLOW_STATE.json 逐步实施知行 P0–P4，嵌入 MetaGPT-X，直至完成或阻塞 |
| **触发** | **立即手动运行**（或 Cron：`0 23 * * *` 每晚 23:00） |
| **仓库** | 你的 GitHub 远程仓库（需先 push `zhixing`） |
| **分支** | `main` |
| **Cloud Agent** | 在 [Cloud Agents 控制台](https://cursor.com/dashboard?tab=cloud-agents) 开启 |
| **工具** | 全部 Agent 工具（Shell、读写文件、终端） |
| **待编辑器完成** | 选择 GitHub 仓库 URL、确认 Cloud 额度、首次 OAuth |

---

## Agent 指令（复制到 Automation → Instructions）

```
你是知行（Zhixing）项目的实施 Agent。工作目录为仓库根目录。

## 必读
- docs/PLAN.md — 里程碑
- docs/STACK.md — 技术选型
- docs/ARCHITECTURE.md — 架构
- docs/METAGPT_INTEGRATION.md — MetaGPT 嵌入
- .cursor/WORKFLOW_STATE.json — 步骤状态机

## 执行规则
1. 读取 WORKFLOW_STATE.json 的 current_step，找到 status=in_progress 的步骤。
2. 执行该步骤 prompt 中的全部工作；写代码、跑命令、修 lint。
3. 完成后：将该 step 标 completed，下一步标 in_progress，更新 current_step。
4. **不要停下来问用户「是否继续」** — 立即执行下一步。
5. auto_continue 为 true 时循环，直到所有 steps completed 或遇到不可恢复错误。
6. MetaGPT-X 在 http://127.0.0.1:8000（若 Cloud 环境无 MetaGPT，跳过联调步骤并记 docs/BLOCKERS.md）。
7. 每完成一个 Phase，更新 docs/PLAN.md 对应勾选。
8. 全部完成后：auto_continue=false，写 docs/RELEASE.md。

## 项目路径约定
- API: services/api (port 8080)
- MetaGPT Bridge: services/metagpt_bridge
- Flutter: apps/mobile
- 基础设施: infra/docker-compose.yml
- MetaGPT 本地: G:\MetaGPT（Cloud 环境改用 API 环境变量）

## 阻塞处理
- Flutter/Docker/LLM 不可用：实现占位 + 文档说明，标记 step completed，继续下一步。
- 不要因单个工具缺失而终止整个流水线。
```

---

## 一键启动（推荐顺序）

### 1. Push 到 GitHub（Cloud Agent 必需）

```powershell
cd G:\方案分析\zhixing
git add -A
git commit -m "chore: zhixing scaffold + overnight workflow"
# 在 GitHub 新建仓库 zhixing 后：
git remote add origin https://github.com/YOUR_USER/zhixing.git
git push -u origin main
```

### 2. 打开 Automations

1. Cursor → **Agents** 窗口（不是普通 Chat）
2. **Automations** → **New Automation**
3. 触发：**Manual** 或 **Schedule** `0 23 * * *`
4. Repo：选刚 push 的 `zhixing`
5. 粘贴上方 **Agent 指令**
6. 启用 **Cloud Agent**
7. **Run now**

### 3. 本地并行（可选，加速 MetaGPT 联调）

Cloud Agent 无法访问你本机 `G:\MetaGPT`，以下仅本地：

```powershell
powershell -File G:\MetaGPT\scripts\start_metagpt_x_api.ps1
powershell -File G:\方案分析\zhixing\scripts\start-api.ps1
```

---

## 与本地 Hook 的区别

| | 本地 Hook | Cloud Agent Automation |
|--|-----------|------------------------|
| 运行环境 | 本机 Cursor 开着 | Cursor 云端 VM |
| 时长 | 会话内最多 ~50 轮 stop | 可跑数小时 |
| 步骤表 | WORKFLOW_STATE.json（32 步） | 同上 |
| MetaGPT | ✅ 可访问 G:\MetaGPT | ❌ 需跳过或远程 API |

---

## Prefill JSON

编辑器若支持 JSON 导入，见同目录 `prefill-workflow.json`。
