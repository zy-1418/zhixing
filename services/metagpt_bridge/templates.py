"""Map 知行 workflow types to MetaGPT SOP idea templates."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

WorkflowType = Literal["research", "writing", "search", "custom"]

_PREFIX: dict[str, str] = {
    "research": "【研究流水线】检索 → 初稿 → 审查 → 校验。",
    "writing": "【写作流水线】大纲 → 起草 → 润色 → 校对。",
    "search": "【检索流水线】检索 → 汇总 → 归档。",
    "custom": "",
}


def build_idea(
    user_instruction: str,
    workflow_type: WorkflowType = "custom",
    *,
    tech_stack: str = "Python FastAPI + Markdown 导出",
    context_snippet: str = "",
) -> str:
    prefix = _PREFIX.get(workflow_type, "")
    parts = [
        prefix,
        f"用户任务：{user_instruction.strip()}",
        f"技术栈：{tech_stack}。",
    ]
    if context_snippet.strip():
        parts.append(f"\n--- 参考上下文 ---\n{context_snippet.strip()}\n---")
    return "\n".join(p for p in parts if p)


def write_spec_file(project_name: str, content: str, metagpt_root: Path) -> Path:
    """Write spec.md for MetaGPT SOP context injection."""
    spec_dir = metagpt_root / "projects" / project_name / "specs" / "001-mvp"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "spec.md"
    spec_path.write_text(content, encoding="utf-8")
    return spec_path
