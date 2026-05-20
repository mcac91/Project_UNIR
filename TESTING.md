# Guía de Pruebas de Validación - Gestor de Tareas API

Este documento describe los procedimientos para validar manualmente todos los endpoints de la API REST.

## Requisitos Previos

- Entorno virtual activado (`venv`)
- Dependencias instaladas (`pip install -r requirements.txt`)
- Servidor ejecutándose en `http://127.0.0.1:8000`

## Instrucciones para Iniciar el Servidor

```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

El servidor estará disponible en `http://127.0.0.1:8000` y la documentación interactiva Swagger en `http://127.0.0.1:8000/docs`.

### Opción 2: Pruebas Manuales usando Swagger UI

1. Abrir en navegador: `http://127.0.0.1:8000/docs`
2. Expandir cada endpoint
3. Hacer clic en "Try it out" y ejecutar

## Casos de Prueba Detallados

### Prueba 1: Crear Tarea (POST /tasks)

**Entrada:**
```json
{
  "title": "Tarea 1",
  "description": "Primera tarea de prueba",
  "priority": "media",
  "effort_hours": 2.5,
  "status": "pendiente",
  "assigned_to": "Ana"
}
```

**Respuesta esperada:** Status 201 Created

**Validar:**
- Status HTTP 201
- Respuesta contiene la tarea creada
- Campos coinciden con los enviados

---

### Prueba 2: Listar Todas las Tareas (GET /tasks)

**URL:** `GET http://127.0.0.1:8000/tasks`

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- Respuesta es un array JSON
- Array contiene todas las tareas creadas

---

### Prueba 3: Obtener Tarea Específica (GET /tasks/{id})

**URL:** `GET http://127.0.0.1:8000/tasks/1`

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- Respuesta es un objeto Task
- El id coincide con el solicitado

---

### Prueba 4: Actualizar Tarea (PUT /tasks/{id})

**URL:** `PUT http://127.0.0.1:8000/tasks/1`

**Entrada:**
```json
{
  "title": "Tarea 1 editada",
  "description": "Descripción modificada",
  "priority": "alta",
  "effort_hours": 3.5,
  "status": "en revisión",
  "assigned_to": "Ana"
}
```

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- Respuesta contiene la tarea actualizada
- Campos actualizados reflejan los nuevos valores

**Nota importante:** Los valores de `priority` y `status` deben ser exactos:

**Priority válidos:**
- "baja"
- "media"
- "alta"
- "bloqueante"

**Status válidos:**
- "pendiente"
- "en progreso"
- "en revisión"
- "completada"

---

### Prueba 5: Eliminar Tarea (DELETE /tasks/{id})

**URL:** `DELETE http://127.0.0.1:8000/tasks/1`

**Respuesta esperada:** Status 204 No Content

**Validar:**
- Status HTTP 204
- Respuesta está vacía
- Verificar con GET /tasks que la tarea ya no existe

---
### Prueba 6: Describir Tarea con IA (POST /ai/tasks/{id}/describe)

**URL:** `POST http://127.0.0.1:8000/ai/tasks/1/describe`

**Descripción:** Genera una descripción con IA y actualiza la tarea.

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- El objeto devuelto contiene `description`
- `description` es un texto no vacío y relevante para la tarea

---

### Prueba 7: Categorizar Tarea con IA (POST /ai/tasks/{id}/categorize)

**URL:** `POST http://127.0.0.1:8000/ai/tasks/1/categorize`

**Descripción:** Clasifica la tarea en una categoría válida.

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- El objeto devuelto contiene `category`
- `category` es uno de: Frontend, Backend, Testing, Infra, Docs, Other

---

### Prueba 8: Estimar Esfuerzo con IA (POST /ai/tasks/{id}/estimate)

**URL:** `POST http://127.0.0.1:8000/ai/tasks/1/estimate`

**Descripción:** Estima el esfuerzo en horas y actualiza `effort_hours`.

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- El objeto devuelto contiene `effort_hours`
- `effort_hours` es un número decimal mayor o igual a 0.5 y menor o igual a 80

---

### Prueba 9: Auditar Tarea con IA (POST /ai/tasks/{id}/audit)

**URL:** `POST http://127.0.0.1:8000/ai/tasks/1/audit`

**Descripción:** Analiza los riesgos y propone mitigación para una tarea.

**Respuesta esperada:** Status 200 OK

**Validar:**
- Status HTTP 200
- El objeto devuelto contiene `risk_analysis` y `risk_mitigation`
- Ambos campos son textos no vacíos con al menos 50 caracteres

---

### Prueba 10: Error 404 en endpoints IA (ID no existente)

**URL:** `POST http://127.0.0.1:8000/ai/tasks/999/describe`

**Respuesta esperada:** Status 404 Not Found

**Validar:**
- Status HTTP 404
- Respuesta contiene mensaje de error

---

### Prueba 11: Probar IA desde Swagger UI

1. Abrir `http://127.0.0.1:8000/docs`
2. Buscar el grupo `ai-tasks`
3. Ejecutar los endpoints `/ai/tasks/{id}/describe`, `/categorize`, `/estimate`, `/audit`
4. Confirmar que la tarea se actualiza en la respuesta y que los campos aparecen en el objeto Task

---
### Prueba 12: Error 404 (Tarea no encontrada)

**URL:** `GET http://127.0.0.1:8000/tasks/999`

**Respuesta esperada:** Status 404 Not Found

**Validar:**
- Status HTTP 404
- Respuesta contiene mensaje de error

---

## Verificación de Persistencia

Después de ejecutar las pruebas:

1. Verificar que `app/data/tasks.json` existe
2. Abrir el archivo y confirmar que contiene los datos en formato JSON
3. Verificar que los cambios se persisten entre reinicios del servidor

## Limpiar Base de Datos para Nuevas Pruebas

```python
from app.services.task_manager import TaskManager

manager = TaskManager()
manager.save_tasks([])
print("Base de datos limpada")
```

---

## Resumen de Endpoints

| Método | Ruta | Propósito | Status Éxito |
|--------|------|----------|-------------|
| POST | /tasks | Crear tarea | 201 |
| GET | /tasks | Listar todas | 200 |
| GET | /tasks/{id} | Obtener una | 200 |
| PUT | /tasks/{id} | Actualizar | 200 |
| DELETE | /tasks/{id} | Eliminar | 204 |
| POST | /ai/tasks/{id}/describe | Generar descripción IA | 200 |
| POST | /ai/tasks/{id}/categorize | Asignar categoría IA | 200 |
| POST | /ai/tasks/{id}/estimate | Estimar esfuerzo IA | 200 |
| POST | /ai/tasks/{id}/audit | Auditoría de riesgos IA | 200 |

