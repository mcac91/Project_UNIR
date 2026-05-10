from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.models.task import Task


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

    def save_tasks(self, tasks: List[Task]) -> None:
        """Guarda la lista de objetos Task en el archivo JSON."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        raw_items = [task.to_dict() for task in tasks]
        self.data_file.write_text(
            json.dumps(raw_items, indent=2, ensure_ascii=False), encoding="utf-8"
        )
