"""Rutas IA para tareas."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.controllers.tasks_controller import TaskController
from app.models.task import Task
from app.services.llm_client import LLMConnectionError, LLMResponseError, LLMTimeoutError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/tasks", tags=["ai-tasks"])
controller = TaskController()



@router.post("/{task_id}/describe", response_model=Task)
async def describe_task(task_id: int) -> Task:
    """Genera una descripción para una tarea existente usando Azure OpenAI y la actualiza."""
    try:
        # Usar el controller para orquestar la operación
        updated_task = controller.describe_task(task_id)
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


@router.post("/{task_id}/categorize", response_model=Task)
async def categorize_task(task_id: int) -> Task:
    """Clasifica una tarea en una categoría predefinida usando Azure OpenAI y la actualiza."""
    try:
        # Usar el controller para orquestar la operación
        updated_task = controller.categorize_task(task_id)
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
