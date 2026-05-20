from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from app.config.prompts import DESCRIBE_TASK_PROMPT
from app.models.task import Task
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class TaskManager:
    """Gestiona la carga y el guardado de tareas en un fichero JSON."""

    def __init__(self, data_file: Path | str | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "data" / "tasks.json"
        self.data_file = Path(data_file) if data_file is not None else default_path

    def load_tasks(self) -> List[Task]:
        """Carga tareas desde el archivo JSON y las convierte en objetos Task."""
        if not self.data_file.exists():
            return []

        content = self.data_file.read_text(encoding="utf-8").strip()
        if not content:
            return []

        try:
            raw_items = json.loads(content)
        except json.JSONDecodeError:
            return []
        return [Task.from_dict(item) for item in raw_items]

    def get_task(self, task_id: int) -> Task:
        """Obtiene una tarea por su ID."""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Tarea con id {task_id} no encontrada")

    def save_tasks(self, tasks: List[Task]) -> None:
        """Guarda la lista de objetos Task en el archivo JSON."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        raw_items = [task.to_dict() for task in tasks]
        self.data_file.write_text(
            json.dumps(raw_items, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def update_task(self, task: Task) -> Task:
        """Actualiza una tarea existente en el almacenamiento."""
        tasks = self.load_tasks()
        for index, existing_task in enumerate(tasks):
            if existing_task.id == task.id:
                tasks[index] = task
                self.save_tasks(tasks)
                logger.info("Tarea %d actualizada", task.id)
                return task
        raise ValueError(f"Tarea con id {task.id} no encontrada")
