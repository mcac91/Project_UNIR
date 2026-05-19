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

    def describe_task(
        self,
        title: str,
        context: str | None = None,
    ) -> str:
        """Genera una descripción de tarea a partir del título y contexto opcional.
        
        Usa el modelo configurado en LLM_MODEL del .env sin forzar un modelo específico.
        """
        title_value = title.strip()
        if not title_value:
            raise ValueError("El título de la tarea es obligatorio")

        context_value = (context or "").strip() or "Sin contexto adicional."
        prompt = DESCRIBE_TASK_PROMPT.format(
            title=title_value,
            context=context_value,
        )

        client = LLMClient()
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente experto en describir tareas técnicas de forma concisa y profesional. "
                    "Devuelve solo la descripción de la tarea, sin encabezados ni explicaciones adicionales."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        # No pasar model explícitamente: let LLMClient use its default_model from .env
        description = client.chat_completion(
            messages=messages,
            temperature=0.5,
            max_completion_tokens=200,
        )

        return description.strip()

    def update_task_description(self, task_id: int, description: str) -> Task:
        """Actualiza la descripción de una tarea existente."""
        tasks = self.load_tasks()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                # Crear copia con descripción actualizada
                updated_task = Task(
                    id=task.id,
                    title=task.title,
                    description=description,
                    priority=task.priority,
                    effort_hours=task.effort_hours,
                    status=task.status,
                    assigned_to=task.assigned_to,
                    category=task.category,
                    risk_analysis=task.risk_analysis,
                    risk_mitigation=task.risk_mitigation,
                )
                tasks[index] = updated_task
                self.save_tasks(tasks)
                logger.info("Tarea %d actualizada con descripción generada por IA", task_id)
                return updated_task
        raise ValueError(f"Tarea con id {task_id} no encontrada")
