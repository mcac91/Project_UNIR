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

ESTIMATE_EFFORT_PROMPT = (
    "Estima el esfuerzo en HORAS de esta tarea técnica.\n"
    "Devuelve SOLO un JSON válido: {{\"hours\": <número>}}\n"
    "Título: {title}\n"
    "Descripción: {description}\n"
    "Categoría: {category}\n"
    "Responde SOLO con el JSON, sin texto adicional."
)

AUDIT_RISK_ANALYSIS_PROMPT = (
    "Analiza los riesgos técnicos de esta tarea en 150-200 palabras.\n"
    "Título: {title}\n"
    "Descripción: {description}\n"
    "Categoría: {category}\n"
    "Esfuerzo estimado: {effort_hours}h\n"
    "Responde con el análisis de riesgos en un texto claro y profesional."
)

AUDIT_RISK_MITIGATION_PROMPT = (
    "Propone estrategias para mitigar estos riesgos en 150-200 palabras.\n"
    "Riesgos identificados: {risk_analysis}\n"
    "Tarea: {title}\n"
    "Esfuerzo estimado: {effort_hours}h\n"
    "Responde con una mitigación práctica y relevante al análisis."
)
