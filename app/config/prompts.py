"""Prompts para las llamadas LLM de IA sobre tareas."""

DESCRIBE_TASK_PROMPT = (
    "Describe en máximo 200 palabras la siguiente tarea técnica de forma concisa y profesional.\n"
    "Título: {title}\n"
    "Contexto adicional: {context}\n"
    "Devuelve solo la descripción de la tarea sin encabezados ni explicaciones adicionales."
)

CATEGORIZE_TASK_PROMPT = (
    "Clasifica la siguiente tarea en UNA SOLA categoría de esta lista: {categories}\n"
    "Título: {title}\n"
    "Descripción: {description}\n"
    "Responde SOLO con el nombre exacto de la categoría de la lista, sin explicaciones adicionales."
)
