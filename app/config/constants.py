"""Constantes y valores por defecto para configuración LLM."""
from __future__ import annotations

DEFAULT_LLM_MODEL = "gpt-5.4-nano"
DEFAULT_LLM_TIMEOUT = 30
DEFAULT_LLM_MAX_RETRIES = 3

# Categorías válidas para tareas
TASK_CATEGORIES = ["Frontend", "Backend", "Testing", "Infra", "Docs", "Other"]

# Categoría por defecto si no se puede clasificar
DEFAULT_CATEGORY = "Other"
