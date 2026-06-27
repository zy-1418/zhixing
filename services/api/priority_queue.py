from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

Priority = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class QueueItem:
    task_id: str
    priority: Priority
    queued_at: datetime


class PriorityQueue:
    """In-process queue skeleton until Redis is available in local/dev."""

    def __init__(self) -> None:
        self._high: deque[QueueItem] = deque()
        self._medium: deque[QueueItem] = deque()
        self._low: deque[QueueItem] = deque()

    def enqueue(self, task_id: str, priority: Priority) -> QueueItem:
        item = QueueItem(task_id=task_id, priority=priority, queued_at=datetime.now(timezone.utc))
        if priority == "high":
            self._high.appendleft(item)
        elif priority == "low":
            self._low.append(item)
        else:
            self._medium.append(item)
        return item

    def snapshot(self) -> dict[str, list[dict[str, str]]]:
        def dump(items: deque[QueueItem]) -> list[dict[str, str]]:
            return [
                {
                    "task_id": item.task_id,
                    "priority": item.priority,
                    "queued_at": item.queued_at.isoformat(),
                }
                for item in items
            ]

        return {
            "backend": "memory-placeholder",
            "high": dump(self._high),
            "medium": dump(self._medium),
            "low": dump(self._low),
        }


priority_queue = PriorityQueue()
