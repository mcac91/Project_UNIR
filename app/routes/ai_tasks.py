"""Rutas IA para tareas."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models.task import Task
from app.services.llm_client import LLMConnectionError, LLMResponseError, LLMTimeoutError
from app.services.task_manager import TaskManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/tasks", tags=["ai-tasks"])
manager = TaskManager()


@router.post("/{task_id}/describe", response_model=Task)
async def describe_task(task_id: int) -> Task:
    """Genera una descripción para una tarea existente usando Azure OpenAI y la actualiza."""
    try:
        # Cargar la tarea existente
        task = manager.get_task(task_id)

        # Generar descripción basada en el título
        generated_description = manager.describe_task(
            title=task.title,
            context=task.description if task.description else None,
        )

        # Actualizar la tarea con la descripción generada
        updated_task = manager.update_task_description(task_id, generated_description)

        return updated_task

    except ValueError as error:
        logger.exception("Error en validación de tarea")
        raise HTTPException(status_code=404, detail=str(error))
    except LLMResponseError as error:
        logger.exception("Error de respuesta LLM")
        raise HTTPException(status_code=502, detail=str(error))
    except LLMTimeoutError as error:
        logger.exception("Timeout en LLM")
        raise HTTPException(status_code=504, detail=str(error))
    except LLMConnectionError as error:
        logger.exception("Error de conexión LLM")
        raise HTTPException(status_code=503, detail=str(error))
