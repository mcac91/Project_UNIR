from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    BLOQUEANTE = "bloqueante"


class Status(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en progreso"
    EN_REVISION = "en revisión"
    COMPLETADA = "completada"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: Priority
    effort_hours: float = Field(..., ge=0)
    status: Status
    assigned_to: str = Field(..., min_length=1)


class TaskCreate(TaskBase):
    """Modelo de entrada para crear una tarea."""
    pass


class Task(TaskBase):
    """Representa una tarea con id en el sistema."""

    id: int = Field(..., ge=1)

    def to_dict(self) -> dict[str, object]:
        """Convierte la tarea a un diccionario serializable."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Task:
        """Crea una instancia de Task a partir de un diccionario."""
        return cls.model_validate(data)
