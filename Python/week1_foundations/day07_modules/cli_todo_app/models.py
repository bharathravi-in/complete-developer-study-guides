"""Task model and operations"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from pathlib import Path


@dataclass
class Task:
    """Represents a single task"""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    
    def complete(self):
        """Mark task as completed"""
        self.completed = True
        self.completed_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary"""
        return cls(**data)
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        priority_icons = {"low": "🔵", "medium": "🟡", "high": "🔴"}
        icon = priority_icons.get(self.priority, "⚪")
        return f"[{status}] {icon} #{self.id} {self.title}"


class TaskManager:
    """Manages task collection with persistence"""
    
    def __init__(self, storage_path: str = "tasks.json"):
        self.storage_path = Path(storage_path)
        self.tasks: List[Task] = []
        self._next_id = 1
        self.load()
    
    def load(self):
        """Load tasks from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                    self._next_id = data.get("next_id", 1)
            except (json.JSONDecodeError, KeyError):
                self.tasks = []
                self._next_id = 1
    
    def save(self):
        """Save tasks to storage"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "next_id": self._next_id
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def add(self, title: str, description: str = "", priority: str = "medium") -> Task:
        """Add a new task"""
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority
        )
        self.tasks.append(task)
        self._next_id += 1
        self.save()
        return task
    
    def get(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def complete(self, task_id: int) -> Optional[Task]:
        """Mark task as completed"""
        task = self.get(task_id)
        if task:
            task.complete()
            self.save()
        return task
    
    def delete(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get(task_id)
        if task:
            self.tasks.remove(task)
            self.save()
            return True
        return False
    
    def list_all(self, show_completed: bool = True) -> List[Task]:
        """List all tasks"""
        if show_completed:
            return self.tasks
        return [t for t in self.tasks if not t.completed]
    
    def list_by_priority(self, priority: str) -> List[Task]:
        """List tasks by priority"""
        return [t for t in self.tasks if t.priority == priority]
    
    def search(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        query = query.lower()
        return [
            t for t in self.tasks
            if query in t.title.lower() or query in t.description.lower()
        ]
    
    def clear_completed(self) -> int:
        """Remove all completed tasks"""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.completed]
        self.save()
        return before - len(self.tasks)
    
    def stats(self) -> dict:
        """Get task statistics"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        
        by_priority = {
            "high": sum(1 for t in self.tasks if t.priority == "high" and not t.completed),
            "medium": sum(1 for t in self.tasks if t.priority == "medium" and not t.completed),
            "low": sum(1 for t in self.tasks if t.priority == "low" and not t.completed),
        }
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "by_priority": by_priority
        }
