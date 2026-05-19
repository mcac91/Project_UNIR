from typing import List

from app.config.constants import TASK_CATEGORIES, DEFAULT_CATEGORY
from app.config.prompts import DESCRIBE_TASK_PROMPT, CATEGORIZE_TASK_PROMPT
from app.models.task import Task, TaskCreate
from app.services.llm_client import LLMClient
from app.services.task_manager import TaskManager


class TaskController:
    """Lógica de negocio para operaciones CRUD de tareas."""

    def __init__(self, manager: TaskManager | None = None) -> None:
        self.manager = manager or TaskManager()

    def list_tasks(self) -> List[Task]:
        return self.manager.load_tasks()

    def get_task(self, task_id: int) -> Task:
        return self.manager.get_task(task_id)

    def create_task(self, task_data: TaskCreate) -> Task:
        tasks = self.manager.load_tasks()
        next_id = max((existing.id for existing in tasks), default=0) + 1
        task = Task(id=next_id, **task_data.model_dump())
        tasks.append(task)
        self.manager.save_tasks(tasks)
        return task

    def update_task(self, task_id: int, task_data: TaskCreate) -> Task:
        tasks = self.manager.load_tasks()
        for index, existing in enumerate(tasks):
            if existing.id == task_id:
                updated_task = Task(id=task_id, **task_data.model_dump())
                tasks[index] = updated_task
                self.manager.save_tasks(tasks)
                return updated_task
        raise ValueError(f"Tarea con id {task_id} no encontrada")

    def delete_task(self, task_id: int) -> None:
        tasks = self.manager.load_tasks()
        filtered = [task for task in tasks if task.id != task_id]
        if len(filtered) == len(tasks):
            raise ValueError(f"Tarea con id {task_id} no encontrada")
        self.manager.save_tasks(filtered)

    def describe_task(self, task_id: int) -> Task:
        """Genera descripción para una tarea existente usando Azure OpenAI."""
        # Obtener tarea
        task = self.manager.get_task(task_id)
        
        # Generar descripción usando LLM
        title_value = task.title.strip()
        context_value = (task.description or "").strip() or "Sin contexto adicional."
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

        description = client.chat_completion(
            messages=messages,
            temperature=0.5,
            max_completion_tokens=200,
        )

        # Actualizar tarea con descripción generada
        updated_task = Task(
            id=task.id,
            title=task.title,
            description=description.strip(),
            priority=task.priority,
            effort_hours=task.effort_hours,
            status=task.status,
            assigned_to=task.assigned_to,
            category=task.category,
            risk_analysis=task.risk_analysis,
            risk_mitigation=task.risk_mitigation,
        )
        
        return self.manager.update_task(updated_task)

    def categorize_task(self, task_id: int) -> Task:
        """Clasifica una tarea en una categoría predefinida usando Azure OpenAI."""
        # Obtener tarea
        task = self.manager.get_task(task_id)
        
        # Generar categoría usando LLM
        categories_str = ", ".join(TASK_CATEGORIES)
        title_value = task.title.strip()
        description_value = (task.description or "").strip() or "Sin descripción"
        
        prompt = CATEGORIZE_TASK_PROMPT.format(
            categories=categories_str,
            title=title_value,
            description=description_value,
        )

        client = LLMClient()
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente experto en clasificar tareas técnicas. "
                    "Devuelve SOLO el nombre exacto de la categoría de la lista proporcionada, sin explicaciones."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        category_response = client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_completion_tokens=50,
        )

        # Validar y limpiar respuesta
        category = category_response.strip()
        if category not in TASK_CATEGORIES:
            # Si no es válida, usar categoría por defecto
            category = DEFAULT_CATEGORY

        # Actualizar tarea con categoría asignada
        updated_task = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            effort_hours=task.effort_hours,
            status=task.status,
            assigned_to=task.assigned_to,
            category=category,
            risk_analysis=task.risk_analysis,
            risk_mitigation=task.risk_mitigation,
        )
        
        return self.manager.update_task(updated_task)
