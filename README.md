# Project_UNIR — Integración IA en API REST

## Resumen rápido
API REST que añade endpoints asistidos por LLM (Azure OpenAI, OpenAI, Anthropic) para describir, categorizar, estimar y auditar tareas.

### Características principales
- ✅ Generación automática de descripciones de tareas
- ✅ Clasificación inteligente en categorías predefinidas
- ✅ Estimación de esfuerzo en horas
- ✅ Análisis de riesgos y propuesta de mitigaciones
- ✅ Arquitectura en capas (Services → Controllers → Routes)
- ✅ Manejo robusto de errores y reintentos
- ✅ Logging estructurado
- ✅ Tests unitarios con pytest

## Instalación rápida

### 1. Clonar y configurar entorno
```bash
git clone <tu_repo>
cd Project_UNIR
python -m venv venv
source venv/Scripts/activate  # En Windows: venv\Scripts\activate
```

### 2. Configurar credenciales
```bash
cp .env.example .env
# Edita .env y rellena: LLM_API_KEY, LLM_ENDPOINT, LLM_PROVIDER
```

**Variables requeridas en `.env`:**
```
LLM_PROVIDER=azure_openai           # Proveedor: azure_openai, openai, anthropic
LLM_API_KEY=<tu_clave_api>          # Tu API key
LLM_ENDPOINT=https://<endpoint>     # URL del endpoint (ej: https://myresource.openai.azure.com/)
LLM_MODEL=gpt-5.4-nano               # Modelo a usar
LLM_TIMEOUT=30                      # Timeout en segundos
LLM_MAX_RETRIES=3                   # Reintentos automáticos
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Validar configuración LLM
```bash
python test_llm_connection.py
```

## Ejecutar la aplicación

### Development con uvicorn
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La API estará disponible en: `http://127.0.0.1:8000`

Docs interactivos (Swagger): `http://127.0.0.1:8000/docs`

## Endpoints principales

### 1. Describir Tarea
```http
POST /ai/tasks/{task_id}/describe
```
Genera una descripción detallada de la tarea usando IA.

**Ejemplo request:**
```json
{
  "task_id": 1,
  "title": "Implementar login OAuth2"
}
```

**Response:**
```json
{
  "task_id": 1,
  "title": "Implementar login OAuth2",
  "description": "Implementación de autenticación OAuth2 integrando con proveedores Google y GitHub. Incluye gestión de tokens, refresh tokens y logout."
}
```

### 2. Categorizar Tarea
```http
POST /ai/tasks/{task_id}/categorize
```
Asigna automáticamente una categoría a la tarea (Frontend, Backend, Testing, Infra, Docs, Other).

**Categorías disponibles:** `Frontend`, `Backend`, `Testing`, `Infra`, `Docs`, `Other`

**Response:**
```json
{
  "task_id": 1,
  "category": "Backend"
}
```

### 3. Estimar Esfuerzo
```http
POST /ai/tasks/{task_id}/estimate
```
Estima el esfuerzo en horas para completar la tarea (rango: 0.5 - 80 horas).

**Response:**
```json
{
  "task_id": 1,
  "effort_hours": 16.5
}
```

### 4. Auditar Tarea (Análisis de Riesgos)
```http
POST /ai/tasks/{task_id}/audit
```
Realiza análisis de riesgos y propone mitigaciones en base a la tarea.

**Response:**
```json
{
  "task_id": 1,
  "risk_analysis": "Riesgos identificados: complejidad de integración OAuth2, posibles fallos de red, necesidad de manejo seguro de tokens...",
  "risk_mitigation": "Mitigación: usar librerías estándar probadas, implementar circuit breakers, validar tokens en cada request..."
}
```

## Tests

### Ejecutar todos los tests
```bash
pytest -q
```

### Ejecutar con cobertura
```bash
pytest --cov=app --cov-report=html
```

### Tests disponibles
- `test_llm_client.py` — Validación del cliente LLM
- `test_task_model.py` — Modelo Task y validaciones
- `test_tasks_describe.py` — Endpoint `/describe`
- `test_tasks_categorize.py` — Endpoint `/categorize`
- `test_tasks_estimate.py` — Endpoint `/estimate`
- `test_tasks_audit.py` — Endpoint `/audit`

## Arquitectura

```
app/
├── config/
│   ├── constants.py       # Constantes globales (categorías, límites)
│   └── prompts.py         # Templates de prompts para LLM
├── models/
│   └── task.py            # Modelo Task con campos IA
├── services/
│   ├── llm_client.py      # Cliente LLM centralizado (retry, errores)
│   └── task_manager.py    # Lógica de describe, categorize, estimate, audit
├── controllers/
│   └── tasks_controller.py # Controller que coordina servicios
├── routes/
│   ├── tasks.py           # Endpoints CRUD originales
│   └── ai_tasks.py        # Endpoints IA (describe, categorize, etc)
└── main.py                # Punto de entrada FastAPI
```

## Archivos de configuración

- `.env` — Credenciales (no incluir en git, usar `.env.example`)
- `.env.example` — Template de variables (incluir en git)
- `requirements.txt` — Dependencias Python
- `pytest.ini` — Configuración de tests
- `.gitignore` — Archivos ignorados (`.env`, `__pycache__`, `.pytest_cache`, etc)

## Troubleshooting

### Error: "LLM_API_KEY not found in .env"
- ✅ Verifica que existe un archivo `.env` en la raíz
- ✅ Copia desde `.env.example` si no existe: `cp .env.example .env`
- ✅ Rellena los valores requeridos

### Error: "Connection timeout"
- ✅ Aumenta `LLM_TIMEOUT` en `.env` (ej: 60)
- ✅ Verifica conectividad a internet y endpoint LLM
- ✅ Revisa credenciales en `.env`

### Tests fallan
- ✅ Ejecuta `python test_llm_connection.py` para validar LLM
- ✅ Verifica que `requirements.txt` está actualizado: `pip install -r requirements.txt --upgrade`
- ✅ Limpia cache: `rm -rf .pytest_cache __pycache__` (Linux/Mac) o `rmdir /s __pycache__ .pytest_cache` (Windows)

## Desarrollo

### Añadir un nuevo endpoint IA
1. Define el prompt en `app/config/prompts.py`
2. Implementa lógica en `app/services/task_manager.py`
3. Crea función controller en `app/controllers/tasks_controller.py`
4. Expón endpoint en `app/routes/ai_tasks.py`
5. Escribe tests en `tests/test_tasks_*.py`

### Cambiar proveedor LLM
Edita `.env` y cambia:
```
LLM_PROVIDER=openai          # Cambiar a: openai, anthropic, etc
LLM_ENDPOINT=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

## Contribuir

- ✅ Seguir [AGENT.md](AGENT.md) para estilo y convenciones
- ✅ Tests requeridos para nuevas funcionalidades
- ✅ Docstrings en funciones públicas
- ✅ Logging en lugar de print()
- ✅ PEP8 compliance

## Licencia
Proyecto académico UNIR
