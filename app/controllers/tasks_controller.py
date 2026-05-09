from typing import List

from app.models.task import Task
from app.services.task_manager import TaskManager


class TaskController:
    """Lógica de negocio para operaciones CRUD de tareas."""

    def __init__(self, manager: TaskManager | None = None) -> None:
        self.manager = manager or TaskManager()

    def list_tasks(self) -> List[Task]:
        return self.manager.load_tasks()

    def get_task(self, task_id: int) -> Task:
        tasks = self.manager.load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Tarea con id {task_id} no encontrada")

    def create_task(self, task: Task) -> Task:
        tasks = self.manager.load_tasks()
        if any(existing.id == task.id for existing in tasks):
            raise ValueError(f"Tarea con id {task.id} ya existe")
        tasks.append(task)
        self.manager.save_tasks(tasks)
        return task

    def update_task(self, task_id: int, task: Task) -> Task:
        tasks = self.manager.load_tasks()
        for index, existing in enumerate(tasks):
            if existing.id == task_id:
                if task.id != task_id:
                    raise ValueError("El id de la tarea no coincide con el id de la ruta")
                tasks[index] = task
                self.manager.save_tasks(tasks)
                return task
        raise ValueError(f"Tarea con id {task_id} no encontrada")

    def delete_task(self, task_id: int) -> None:
        tasks = self.manager.load_tasks()
        filtered = [task for task in tasks if task.id != task_id]
        if len(filtered) == len(tasks):
            raise ValueError(f"Tarea con id {task_id} no encontrada")
        self.manager.save_tasks(filtered)
