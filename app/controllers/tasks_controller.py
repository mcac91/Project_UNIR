import json
import logging
import re
from typing import List

from app.config.constants import TASK_CATEGORIES, DEFAULT_CATEGORY
from app.config.prompts import (
    AUDIT_RISK_ANALYSIS_PROMPT,
    AUDIT_RISK_MITIGATION_PROMPT,
    CATEGORIZE_TASK_PROMPT,
    DESCRIBE_TASK_PROMPT,
    ESTIMATE_EFFORT_PROMPT,
)
from app.models.task import Task, TaskCreate
from app.services.llm_client import LLMClient, LLMResponseError
from app.services.task_manager import TaskManager

logger = logging.getLogger(__name__)


def parse_effort_response(response: str) -> float:
    """Parsea la respuesta LLM para extraer horas estimadas.
    
    Soporta: JSON válido, regex fallback, o búsqueda de número.
    
    Args:
        response: Respuesta del LLM.
        
    Returns:
        float: Horas estimadas (0.5 ≤ hours ≤ 80).
        
    Raises:
        ValueError: Si no se puede extraer un valor válido.
    """
    if not response or not response.strip():
        raise ValueError("Respuesta LLM vacía")
    
    response = response.strip()
    logger.debug(f"Parseando respuesta de esfuerzo: {response}")
    
    # Intento 1: Parsear JSON
    try:
        data = json.loads(response)
        hours = float(data.get("hours", 0))
        if 0.5 <= hours <= 80:
            logger.info(f"Esfuerzo parseado desde JSON: {hours}h")
            return hours
        else:
            logger.warning(f"Horas JSON fuera de rango: {hours}")
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        logger.debug(f"JSON parsing falló: {error}")
    
    # Intento 2: Regex para buscar "N horas"
    match = re.search(r'(\d+\.?\d*)\s*horas?', response, re.IGNORECASE)
    if match:
        hours = float(match.group(1))
        if 0.5 <= hours <= 80:
            logger.info(f"Esfuerzo parseado desde regex: {hours}h")
            return hours
        else:
            logger.warning(f"Horas regex fuera de rango: {hours}")
    
    # Intento 3: Buscar cualquier número
    numbers = re.findall(r'\d+\.?\d*', response)
    if numbers:
        hours = float(numbers[0])
        if 0.5 <= hours <= 80:
            logger.info(f"Esfuerzo parseado desde número: {hours}h")
            return hours
        else:
            logger.warning(f"Horas número fuera de rango: {hours}")
    
    raise ValueError(f"No se pudo extraer horas válidas de: {response}")


def validate_audit_text(text: str, field_name: str) -> str:
    """Valida el texto de auditoría para asegurar longitud mínima y contenido."""
    if not text or not text.strip():
        raise ValueError(f"{field_name} no puede estar vacío")

    cleaned = text.strip()
    if len(cleaned) < 50:
        raise ValueError(f"{field_name} debe tener al menos 50 caracteres")

    return cleaned


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

    def _validate_audit_inputs(self, task: Task) -> None:
        if not task.title or not task.title.strip():
            raise ValueError("Tarea debe tener title para auditar")
        if not task.description or not task.description.strip():
            raise ValueError("Tarea debe tener description para auditar")
        if not task.category or not task.category.strip():
            raise ValueError("Tarea debe tener category para auditar")
        if task.effort_hours <= 0:
            raise ValueError("Tarea debe tener effort_hours mayor a 0 para auditar")

    def _generate_audit_text(self, messages: list[dict[str, str]], field_name: str) -> str:
        last_error: Exception | None = None
        client = LLMClient()

        for attempt in range(2):
            response = client.chat_completion(
                messages=messages,
                temperature=0.4,
                max_completion_tokens=250,
            )
            try:
                return validate_audit_text(response, field_name)
            except ValueError as error:
                last_error = error
                logger.warning(
                    "Validación de %s falló en intento %d: %s",
                    field_name,
                    attempt + 1,
                    error,
                )

        raise LLMResponseError(
            f"No se pudo generar {field_name} válido tras varios intentos: {last_error}"
        )

    def _analyze_risks(self, task: Task) -> str:
        prompt = AUDIT_RISK_ANALYSIS_PROMPT.format(
            title=task.title.strip(),
            description=task.description.strip(),
            category=task.category.strip() or DEFAULT_CATEGORY,
            effort_hours=task.effort_hours,
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente experto en análisis de riesgos técnicos. "
                    "Genera un análisis objetivo y claro de los riesgos asociados a la tarea."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        return self._generate_audit_text(messages, "risk_analysis")

    def _mitigate_risks(self, task: Task, risk_analysis: str) -> str:
        prompt = AUDIT_RISK_MITIGATION_PROMPT.format(
            title=task.title.strip(),
            risk_analysis=risk_analysis.strip(),
            effort_hours=task.effort_hours,
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente experto en mitigación de riesgos técnicos. "
                    "Propón acciones prácticas para reducir los riesgos identificados."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        return self._generate_audit_text(messages, "risk_mitigation")

    def audit_task(self, task_id: int) -> Task:
        """Analiza riesgos y propone mitigación para una tarea existente."""
        task = self.manager.get_task(task_id)
        self._validate_audit_inputs(task)

        risk_analysis = self._analyze_risks(task)
        risk_mitigation = self._mitigate_risks(task, risk_analysis)

        updated_task = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            effort_hours=task.effort_hours,
            status=task.status,
            assigned_to=task.assigned_to,
            category=task.category,
            risk_analysis=risk_analysis,
            risk_mitigation=risk_mitigation,
        )
        return self.manager.update_task(updated_task)

    def estimate_effort(self, task_id: int) -> Task:
        """Estima el esfuerzo en horas para una tarea usando Azure OpenAI."""
        # Obtener tarea
        task = self.manager.get_task(task_id)
        
        # Validar campos requeridos
        if not task.title or not task.description:
            error_msg = "Tarea debe tener title y description para estimar esfuerzo"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generar estimación usando LLM
        title_value = task.title.strip()
        description_value = task.description.strip()
        category_value = task.category or DEFAULT_CATEGORY
        
        prompt = ESTIMATE_EFFORT_PROMPT.format(
            title=title_value,
            description=description_value,
            category=category_value,
        )
        
        client = LLMClient()
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un experto en estimación de esfuerzo técnico."
                    "El número de horas debe ser un valor decimal entre 0.5 y 80, representando el esfuerzo total requerido para completar la tarea. "
                    "Responde SOLO con JSON válido: {\"hours\": <número>}"
                ),
            },
            {"role": "user", "content": prompt},
        ]
        
        response = client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_completion_tokens=100,
        )
        
        # Parsear respuesta
        effort_hours = parse_effort_response(response)
        logger.info(f"Esfuerzo estimado para tarea {task_id}: {effort_hours}h")
        
        # Actualizar tarea con horas estimadas
        updated_task = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            effort_hours=effort_hours,
            status=task.status,
            assigned_to=task.assigned_to,
            category=task.category,
            risk_analysis=task.risk_analysis,
            risk_mitigation=task.risk_mitigation,
        )
        
        return self.manager.update_task(updated_task)

