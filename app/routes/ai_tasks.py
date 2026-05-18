"""Rutas IA para tareas."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.task import Priority, Status
from app.services.llm_client import LLMConnectionError, LLMResponseError, LLMTimeoutError
from app.services.task_manager import TaskManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/tasks", tags=["ai-tasks"])
manager = TaskManager()


class TaskDescribeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    category: str | None = None
    priority: Priority | None = None
    effort_hours: float | None = Field(default=None, ge=0)
    status: Status | None = None
    assigned_to: str | None = Field(default=None, min_length=1)


class TaskDescribeResponse(BaseModel):
    title: str
    description: str
    category: str | None = None
    priority: Priority | None = None
    effort_hours: float | None = None
    status: Status | None = None
    assigned_to: str | None = None


@router.post("/describe", response_model=TaskDescribeResponse)
async def describe_task(request: TaskDescribeRequest) -> TaskDescribeResponse:
    """Genera una descripción de tarea usando un modelo LLM de Azure OpenAI."""
    try:
        generated_description = manager.describe_task(
            title=request.title,
            context=request.description,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except LLMResponseError as error:
        logger.exception("Error de respuesta LLM")
        raise HTTPException(status_code=502, detail=str(error))
    except LLMTimeoutError as error:
        logger.exception("Timeout en LLM")
        raise HTTPException(status_code=504, detail=str(error))
    except LLMConnectionError as error:
        logger.exception("Error de conexión LLM")
        raise HTTPException(status_code=503, detail=str(error))

    payload = request.model_dump(exclude={"description"})
    payload["description"] = generated_description
    return TaskDescribeResponse(**payload)
