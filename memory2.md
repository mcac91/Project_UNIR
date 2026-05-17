# Memory2.md - Desarrollo Entregable 2: Integración IA en API REST

**Proyecto:** Integración de Endpoints de IA en API REST existente  
**Fecha inicio:** 17/05/2026  
**Estado:** En Preparación  

---

## Contexto y Normas

Este documento guía el desarrollo paso a paso del **Entregable 2**.

### Normas a cumplir (AGENT.md)
- ✅ Código claro y mantenible (prioridad: claridad > mantenibilidad > corrección > performance)
- ✅ PEP8 + 4 espacios de indentación
- ✅ Naming: `snake_case` funciones/variables, `PascalCase` clases, `UPPER_CASE` constantes
- ✅ Type hints en funciones públicas
- ✅ Docstrings en todas las funciones públicas
- ✅ Funciones cortas (<30 líneas), máximo 1 responsabilidad
- ✅ Imports ordenados: stdlib → third-party → local
- ✅ Logging en lugar de print
- ✅ Tests con pytest (`test_*.py`)
- ✅ Sin secrets en el código (usar `.env`)

---

## Fases de Desarrollo

### Fase 1: Preparación del Entorno ⏳ (0.5 días)

**Objetivo:** Verificar entorno, instalar dependencias, configurar LLM.

#### Tasks
- [ ] **1.1** Verificar Python 3.9+ y virtualenv activado
- [ ] **1.2** Instalar dependencias en `requirements.txt`:
  - `openai` o `azure-openai` (según LLM elegido)
  - `python-dotenv` (gestión de `.env`)
  - `flask` o `fastapi` (ya existente)
  - Resto: flask/fastapi auxiliares
- [ ] **1.3** Crear fichero `.env` con variables (NO incluir en git):
  ```
  LLM_PROVIDER=azure_openai  # o openai, anthropic
  LLM_API_KEY=<tu_api_key>
  LLM_ENDPOINT=<tu_endpoint>
  LLM_MODEL=gpt-4o-mini
  LLM_TIMEOUT=30
  ```
- [ ] **1.4** Crear `.env.example` para documentar variables (sin valores reales)
- [ ] **1.5** Crear script `test_llm_connection.py` que valide:
  - Carga de variables de `.env`
  - Conexión al modelo LLM
  - Respuesta correcta de prueba simple
- [ ] **1.6** Ejecutar y validar script

**Punto de validación:** El usuario ejecuta `python test_llm_connection.py` y recibe respuesta satisfactoria del LLM.

---

### Fase 2: Actualización del Modelo Task ⏳ (0.5 días)

**Objetivo:** Añadir campos `category`, `risk_analysis`, `risk_mitigation` al modelo Task.

#### Tasks
- [ ] **2.1** Actualizar modelo ORM/Pydantic en `app/models/task.py`:
  - Añadir `category: str` (p.ej. Frontend, Backend, Testing, Infra)
  - Añadir `risk_analysis: str` (texto largo, optional)
  - Añadir `risk_mitigation: str` (texto largo, optional)
- [ ] **2.2** Actualizar esquema de validación (Pydantic) si existe
- [ ] **2.3** Ajustar base de datos:
  - Si SQLAlchemy: crear migración o recrear tabla
  - Si JSON/mock: adaptar estructura
- [ ] **2.4** Actualizar endpoints CRUD existentes (GET, POST, PUT) para aceptar nuevos campos
- [ ] **2.5** Escribir tests unitarios en `test_task_model.py`:
  - Crear Task con nuevos campos
  - Validar valores por defecto
  - Validar tipos

**Punto de validación:** El usuario verifica que:
- El CRUD original sigue funcionando
- Los nuevos campos se guardan/recuperan correctamente
- Los tests pasan sin errores

---

### Fase 3: Módulo Client LLM ⏳ (1 día)

**Objetivo:** Crear cliente centralizado para llamadas LLM con manejo robusto de errores.

#### Tasks
- [ ] **3.1** Crear `app/services/llm_client.py` con:
  - Clase `LLMClient` (o funciones modulares si prefieres)
  - Métodos para llamadas básicas
  - Manejo de timeouts
  - Retry logic (máx 3 intentos)
  - Logs estructurados (no prints)
  - Validación de respuestas
- [ ] **3.2** Gestión de configuración:
  - Cargar del `.env`
  - Validar variables requeridas al iniciar
  - Usar enums/constantes para valores comunes
- [ ] **3.3** Manejo de errores específicos:
  - `LLMConnectionError`
  - `LLMResponseError`
  - `LLMTimeoutError`
- [ ] **3.4** Tests en `test_llm_client.py`:
  - Mock de respuestas LLM
  - Validar retry logic
  - Casos de error

**Punto de validación:** El usuario verifica que:
- El cliente se inicializa correctamente
- Las llamadas al LLM se ejecutan sin errores
- Los reintentos funcionan
- Los logs son informativos

---

### Fase 4: Endpoint `/ai/tasks/describe` ⏳ (0.5 días)

**Objetivo:** Implementar generación de descripción por IA.

#### Tasks
- [ ] **4.1** Crear endpoint POST en `app/routes/tasks.py` o archivo separado:
  - Ruta: `/ai/tasks/describe`
  - Input: Task con `title` y opcionalmente otros campos
  - Output: Task con `description` generada
- [ ] **4.2** Implementar función `describe_task()` en `app/services/task_manager.py`:
  - Validar que `title` no esté vacío
  - Preparar prompt específico
  - Llamar a `LLMClient`
  - Actualizar objeto Task
  - Guardar en BD si aplica
- [ ] **4.3** Definir prompt template en constante (`app/config/prompts.py`):
  ```
  "Describe en máximo 200 palabras una tarea: {title}. 
   Contexto: {context}. Sé conciso y profesional."
  ```
- [ ] **4.4** Tests en `test_tasks_describe.py`:
  - Test con input válido
  - Test sin title (debe fallar)
  - Test con respuesta vacía del LLM
- [ ] **4.5** Documentar en README o Swagger

**Punto de validación:** El usuario verifica que:
- El endpoint responde correctamente en Postman
- La descripción generada es coherente
- Los tests pasan

---

### Fase 5: Endpoint `/ai/tasks/categorize` ⏳ (0.5 días)

**Objetivo:** Clasificar tarea en categoría predefinida.

#### Tasks
- [ ] **5.1** Definir lista de categorías válidas (constante en `app/config/constants.py`):
  ```python
  TASK_CATEGORIES = ["Frontend", "Backend", "Testing", "Infra", "Docs", "Other"]
  ```
- [ ] **5.2** Crear endpoint POST `/ai/tasks/categorize`:
  - Input: Task con `title` + `description` (opcional)
  - Output: Task con `category` asignada
- [ ] **5.3** Implementar función `categorize_task()`:
  - Prompt forzando JSON con categoría válida
  - Validar que respuesta esté en lista permitida
  - Si no válida: retry o asignar "Other"
  - Actualizar Task y guardar
- [ ] **5.4** Prompt template (`app/config/prompts.py`):
  ```
  "Clasifica esta tarea en UNA SOLA categoría: {categories}
   Tarea: {title} - {description}
   Responde SOLO con el nombre de la categoría."
  ```
- [ ] **5.5** Tests en `test_tasks_categorize.py`:
  - Validar categoría válida
  - Validar categoría inválida (retry/default)
  - Tests de parsing

**Punto de validación:** El usuario verifica que:
- La categoría asignada es correcta
- Las categorías inválidas se manejan bien
- Swagger/Postman muestra correctamente

---

### Fase 6: Endpoint `/ai/tasks/estimate` ⏳ (1 día)

**Objetivo:** Estimar esfuerzo en horas mediante IA.

#### Tasks
- [ ] **6.1** Crear endpoint POST `/ai/tasks/estimate`:
  - Input: Task con `title`, `description`, `category`
  - Output: Task con `effort_hours` (float)
- [ ] **6.2** Implementar función `estimate_effort()`:
  - Validar campos requeridos
  - Prompt pidiendo salida JSON con `{"hours": <número>}`
  - Parsing seguro a float
  - Validar rango: 0.5 ≤ hours ≤ 80
  - Actualizar Task
- [ ] **6.3** Prompt template:
  ```
  "Estima el esfuerzo en HORAS de esta tarea.
   Devuelve SOLO un JSON: {\"hours\": <número>}
   Tarea: {title}
   Descripción: {description}
   Categoría: {category}
   Responde SOLO con el JSON, sin texto adicional."
  ```
- [ ] **6.4** Función auxiliar `parse_effort_response()` con:
  - Parsing robusto (JSON, regex, fallback)
  - Validación de rango
  - Manejo de excepciones
- [ ] **6.5** Tests en `test_tasks_estimate.py`:
  - Parsing JSON válido
  - Parsing inválido (fallback)
  - Rango fuera de límites
  - Task sin campos requeridos

**Punto de validación:** El usuario verifica que:
- Las horas estimadas son números válidos
- El rango es correcto
- El parsing maneja casos inválidos
- Postman muestra respuesta coherente

---

### Fase 7: Endpoint `/ai/tasks/audit` ⏳ (1 día)

**Objetivo:** Analizar riesgos y proponer mitigación (dos llamadas LLM).

#### Tasks
- [ ] **7.1** Crear endpoint POST `/ai/tasks/audit`:
  - Input: Task con todos los campos
  - Output: Task con `risk_analysis` + `risk_mitigation` completos
- [ ] **7.2** Implementar función `audit_task()`:
  - **Primera llamada:** `analyze_risks()` → genera `risk_analysis`
  - **Segunda llamada:** `mitigate_risks()` → genera `risk_mitigation` basada en analysis
  - Ambas se guardan en el objeto Task
- [ ] **7.3** Prompt templates:
  ```
  # Análisis de riesgos
  "Analiza los riesgos técnicos de esta tarea en 150-200 palabras:
   {title} - {description}
   Categoría: {category}, Esfuerzo: {effort_hours}h"
   
  # Mitigación
  "Propone estrategias para mitigar estos riesgos (150-200 palabras):
   Riesgos identificados: {risk_analysis}
   Tarea: {title}, Esfuerzo: {effort_hours}h"
  ```
- [ ] **7.4** Validación mínima:
  - Ambos campos no vacíos
  - Longitud mínima (50 caracteres)
  - Si validation falla: logging y retry
- [ ] **7.5** Tests en `test_tasks_audit.py`:
  - Audit completo válido
  - Respuesta LLM parcial
  - Task sin campos requeridos
  - Validación de minimos

**Punto de validación:** El usuario verifica que:
- Se generan riesgos coherentes
- La mitigación es relevante a los riesgos
- Ambos campos se guardan
- Manejo de errores correcto

---

### Fase 8: Pruebas Integrales + Documentación ⏳ (1 día)

**Objetivo:** Validación end-to-end, documentación y empaquetado.

#### Tasks
- [ ] **8.1** Pruebas manuales en Postman/Swagger:
  - ✅ CRUD Task original (GET, POST, PUT, DELETE)
  - ✅ `/describe` con description vacía
  - ✅ `/categorize` sin category
  - ✅ `/estimate` sin effort_hours
  - ✅ `/audit` completo
  - ✅ Casos límite: input vacío, campos faltantes
- [ ] **8.2** Verificar CRUD sigue funcionando sin degradación
- [ ] **8.3** Cobertura de tests:
  - Todos los endpoints tienen test
  - Tests de error incluidos
  - Coverage ≥ 80% en lógica crítica
- [ ] **8.4** Documentación:
  - README.md actualizado con ejemplos de uso
  - `.env.example` incluido (sin secretos)
  - Docstrings en funciones públicas
  - Prompts documentados en `app/config/prompts.py`
- [ ] **8.5** Revisar código contra AGENT.md:
  - ✅ PEP8 compliance
  - ✅ Naming conventions
  - ✅ Type hints
  - ✅ Sin hardcoded secrets
  - ✅ Logging adecuado
  - ✅ Funciones cortas
- [ ] **8.6** Limpieza:
  - Eliminar archivos de debug
  - Actualizar `.gitignore` (`.env`, `__pycache__`, `.pytest_cache`)
  - Verificar `requirements.txt` actualizado
- [ ] **8.7** Empaquetar:
  - Crear `.zip` con proyecto completo
  - Incluir colección Postman (opcional)
  - README en raíz

**Punto de validación:** El usuario verifica que:
- Todos los endpoints funcionan en Postman
- Código cumple AGENT.md
- Tests pasan y coverage es adecuado
- Documentación es clara
- `.zip` está listo para entrega

---

## Checklist de Validación por Fases

### ✅ Fase 1 - Preparación
- [ ] Script `test_llm_connection.py` ejecutado exitosamente
- [ ] `.env` configurado con credenciales válidas
- [ ] Dependencias instaladas (`pip freeze` actualizado)

### ✅ Fase 2 - Modelo Task
- [ ] Nuevos campos en modelo Task
- [ ] CRUD original funciona con nuevos campos
- [ ] Tests de modelo pasan

### ✅ Fase 3 - LLM Client
- [ ] Cliente se inicializa sin errores
- [ ] Llamadas al LLM funcionan
- [ ] Retry logic probado
- [ ] Tests de cliente pasan

### ✅ Fase 4 - `/describe`
- [ ] Endpoint responde en Postman
- [ ] Descripción coherente
- [ ] Manejo de errores funciona
- [ ] Tests pasan

### ✅ Fase 5 - `/categorize`
- [ ] Endpoint responde con categoría válida
- [ ] Casos inválidos manejados
- [ ] Tests pasan
- [ ] Validación en Postman

### ✅ Fase 6 - `/estimate`
- [ ] Endpoint devuelve horas en rango válido
- [ ] Parsing de respuestas LLM funciona
- [ ] Tests de parsing pasan
- [ ] Validado en Postman

### ✅ Fase 7 - `/audit`
- [ ] Riesgos generados correctamente
- [ ] Mitigación coherente a riesgos
- [ ] Ambos campos guardados
- [ ] Tests pasan
- [ ] Validado en Postman

### ✅ Fase 8 - Finales
- [ ] Todas pruebas manuales pasadas
- [ ] Código cumple AGENT.md
- [ ] Documentación completa
- [ ] `.zip` listo para entrega
- [ ] Tests con coverage ≥80%

---

## Notas de Desarrollo

### Archivos a crear/modificar
```
app/
├── config/
│   ├── __init__.py
│   ├── constants.py          (TASK_CATEGORIES, etc.)
│   └── prompts.py            (Todos los prompts LLM)
├── services/
│   ├── llm_client.py         (Cliente LLM centralizado)
│   └── task_manager.py       (Funciones describe, categorize, estimate, audit)
├── routes/
│   └── tasks.py              (Endpoints /ai/tasks/*)
└── models/
    └── task.py               (Actualizar modelo)

tests/
├── test_llm_client.py
├── test_task_model.py
├── test_tasks_describe.py
├── test_tasks_categorize.py
├── test_tasks_estimate.py
└── test_tasks_audit.py

.env.example
requirements.txt              (actualizar)
README.md                      (actualizar)
```

### Principios clave
1. **Validación usuario:** Cada fase requiere validación explícita antes de avanzar
2. **AGENT.md:** Cumplir reglas de estilo y seguridad desde inicio
3. **Testing:** Tests desde el inicio, no al final
4. **Logging:** Usar `logging` siempre, sin `print()`
5. **Errores:** Específicos, no genéricos (`except Exception`)
6. **Documentación:** Docstrings + comentarios en lógica compleja

---

## Estado Actual

| Fase | Estado | Notas |
|------|--------|-------|
| 1 - Preparación | ⏳ PENDIENTE | Espera validación usuario |
| 2 - Modelo Task | ⏳ PENDIENTE | Depende de Fase 1 ✅ |
| 3 - LLM Client | ⏳ PENDIENTE | Depende de Fase 2 ✅ |
| 4 - `/describe` | ⏳ PENDIENTE | Depende de Fase 3 ✅ |
| 5 - `/categorize` | ⏳ PENDIENTE | Depende de Fase 3 ✅ |
| 6 - `/estimate` | ⏳ PENDIENTE | Depende de Fase 3 ✅ |
| 7 - `/audit` | ⏳ PENDIENTE | Depende de Fase 3 ✅ |
| 8 - Finales | ⏳ PENDIENTE | Depende de 4-7 ✅ |

---

**Próximo paso:** Ejecutar Fase 1 y validación usuario
