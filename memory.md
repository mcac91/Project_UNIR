# Memoria del Proyecto - Gestor de Tareas (Entregable 1)

## Descripción General

Este documento sirve como memoria del proyecto basado en la planificación técnica definida en `plan.md`. El objetivo es desarrollar una API REST para la gestión de tareas asignadas a usuarios, utilizando FastAPI en lugar de Flask por motivos de escalabilidad y mantenibilidad.

El proyecto se llevará a cabo siguiendo estrictamente las reglas definidas en `AGENT.md - Python Style Guide`, priorizando claridad, mantenibilidad y consistencia en el código Python.

## Plan de Trabajo Paso a Paso

A continuación, se detalla el plan de desarrollo dividido en pasos secuenciales. Cada paso incluye una checklist de subtareas que deben completarse y validarse antes de avanzar al siguiente. No se procederá al paso siguiente hasta que el desarrollador confirme la validación de todas las subtareas del paso actual.

### Paso 1: Preparación del Entorno
- [x] Crear entorno virtual (`venv`)
- [x] Instalar dependencias necesarias (FastAPI, Uvicorn, Pydantic)
- [x] Generar `requirements.txt` con las dependencias instaladas

**Validación requerida:** Verificar que el entorno virtual esté activado y que las dependencias se instalen correctamente sin errores.

### Paso 2: Crear Arquitectura del Proyecto
- [x] Crear carpetas base: `app/routes/`, `app/controllers/`, `app/models/`, `app/services/`, `app/data/`
- [x] Configurar punto de entrada (`app/main.py`) con la aplicación FastAPI básica

**Validación requerida:** Confirmar que la estructura de carpetas existe y que `main.py` se ejecuta sin errores, mostrando la documentación Swagger básica.

### Paso 3: Implementar Modelo `Task`
- [x] Definir la clase `Task` en `app/models/task.py` con todos los atributos requeridos (id, title, description, priority, effort_hours, status, assigned_to)
- [x] Implementar método `to_dict()` para convertir el objeto a diccionario
- [x] Implementar método `from_dict()` para crear un objeto Task a partir de un diccionario

**Validación requerida:** Crear una instancia de Task, convertirla a dict y viceversa, verificando que los tipos y valores sean correctos.

### Paso 4: Implementar `TaskManager`
- [x] Crear la clase `TaskManager` en `app/services/task_manager.py`
- [x] Implementar método estático `load_tasks()` para cargar tareas desde `app/data/tasks.json` y convertirlas en objetos Task
- [x] Implementar método estático `save_tasks()` para guardar la lista de objetos Task en el archivo JSON
- [x] Asegurar manejo correcto de lectura/escritura en `tasks.json`, incluyendo casos de archivo vacío o inexistente

**Validación requerida:** Probar carga y guardado de tareas, verificando que el archivo JSON se actualice correctamente y que los datos se mantengan consistentes.

### Paso 5: Implementar Endpoints CRUD
- [ ] Crear archivo de rutas `app/routes/tasks.py` con los endpoints definidos (POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id})
- [ ] Crear controlador `app/controllers/tasks_controller.py` para manejar la lógica de petición/respuesta
- [ ] Conectar rutas con el controlador y el controlador con `TaskManager`

**Validación requerida:** Probar cada endpoint individualmente mediante requests HTTP, verificando respuestas JSON correctas y manejo de errores (ej. tarea no encontrada).

### Paso 6: Validación Final
- [ ] Probar todos los endpoints en conjunto para asegurar integración completa
- [ ] Verificar persistencia correcta en JSON tras operaciones CRUD
- [ ] Comprobar formato correcto de respuestas JSON y cumplimiento de la API REST
- [ ] Ejecutar pruebas manuales exhaustivas para cubrir casos edge (IDs inexistentes, datos inválidos, etc.)

**Validación requerida:** La aplicación debe ser completamente funcional, con todos los endpoints operativos y datos persistiendo correctamente en `tasks.json`.

## Notas Adicionales

- **Estilo de Código:** Todo el código debe adherirse al `AGENT.md - Python Style Guide`, incluyendo PEP8, tipado fuerte, docstrings, y estructura modular.
- **Validación Continua:** Antes de marcar una subtarea como completada, ejecutar pruebas básicas y revisar el código por cumplimiento de estándares.
- **Documentación:** Mantener este archivo actualizado con el progreso real, marcando checklists a medida que se completen.
- **Evolución Futura:** La arquitectura debe ser extensible para futuras capas (autenticación, BD avanzada, etc.), como se indica en `plan.md`.

## Estado del Proyecto

- **Inicio:** [Fecha actual]
- **Progreso:** Paso 4 completado. `TaskManager` implementado.
- **Próximo Paso:** Paso 5 - Implementar Endpoints CRUD.