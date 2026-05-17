# Planificación del Proyecto (Entregable 2)  
**Proyecto:** Integración de Endpoints de IA en API REST existente (Flask/FastAPI)  
**Contexto:** Segunda parte del proyecto (continuación del CRUD Task del Entregable 1)  

---

## 1. Objetivo general
Integrar funcionalidades basadas en LLMs dentro de la API REST existente, ampliando el modelo **Task** y creando nuevos endpoints que automaticen:
- Generación de descripciones.
- Clasificación por categorías.
- Estimación de esfuerzo en horas.
- Auditoría de riesgos y mitigación.

---

## 2. Alcance del entregable
### 2.1. Funcionalidades obligatorias
- Extensión del modelo `Task` con nuevos campos.
- Implementación de 4 endpoints IA:
  - `/ai/tasks/describe`
  - `/ai/tasks/categorize`
  - `/ai/tasks/estimate`
  - `/ai/tasks/audit`
- Integración con un proveedor LLM (Azure OpenAI recomendado, OpenAI/Anthropic alternativo).
- Pruebas manuales con Postman / Swagger.

### 2.2. Entregables finales
- Proyecto completo en formato `.zip` con:
  - Código fuente completo.
  - (Opcional) colección Postman.

---

## 3. Requisitos previos
### 3.1. Requisitos técnicos
- Proyecto base del Entregable 1 (API Flask o FastAPI con CRUD Task funcionando).
- Python instalado y entorno virtual configurado.
- Dependencias instaladas:
  - `openai` (o SDK alternativo)
  - framework API (Flask/FastAPI)
  - librerías auxiliares (pydantic/sqlalchemy según proyecto)

### 3.2. Requisitos de configuración
- Credenciales válidas de proveedor LLM:
  - `API_KEY`
  - `ENDPOINT`
  - `MODEL_NAME`
- Variables configuradas en `.env` o configuración segura.

---

## 4. Modelo de datos: Task (actualización)
### 4.1. Campos existentes
- `id`
- `title`
- `description`
- `priority`
- `effort_hours`
- `status`
- `assigned_to`

### 4.2. Nuevos campos a añadir
- `category` *(string o enum)*
- `risk_analysis` *(texto largo)*
- `risk_mitigation` *(texto largo)*

### 4.3. Tareas técnicas asociadas
- Modificar modelo ORM / esquema Pydantic.
- Ajustar migraciones o recreación de base de datos.
- Actualizar endpoints CRUD si requieren adaptación.

---

## 5. Endpoints IA (nuevas funcionalidades)
### 5.1. POST `/ai/tasks/describe`
**Entrada:** Task con `description` vacía.  
**Salida:** Task con `description` generada mediante LLM.  

**Acciones técnicas:**
- Definir prompt con `title` y resto de campos.
- Validar que `description` esté vacío o sea opcional.
- Devolver el objeto Task actualizado.

---

### 5.2. POST `/ai/tasks/categorize`
**Entrada:** Task sin categoría.  
**Salida:** Task con `category` asignada por clasificación LLM.  

**Acciones técnicas:**
- Definir listado de categorías posibles: Frontend, Backend, Testing, Infra, etc.
- Diseñar prompt para forzar salida en formato controlado.
- Validar respuesta y asignar categoría.

---

### 5.3. POST `/ai/tasks/estimate`
**Entrada:** Task sin `effort_hours`.  
**Salida:** Task con `effort_hours` (valor numérico).  

**Acciones técnicas:**
- Prompt basado en `title`, `description`, `category`.
- Pedir al modelo respuesta en JSON o formato numérico estricto.
- Implementar parsing robusto a `float` o `int`.
- Validación de rango razonable.

---

### 5.4. POST `/ai/tasks/audit`
**Entrada:** Task con todos los campos excepto:
- `risk_analysis`
- `risk_mitigation`

**Salida:** Task con:
- `risk_analysis` generado
- `risk_mitigation` generado

**Acciones técnicas:**
- Primera llamada LLM: análisis de riesgos.
- Segunda llamada LLM: mitigación basada en riesgos + task.
- Guardar ambas respuestas en campos separados.
- Validar contenido mínimo antes de devolver.

---

## 6. Integración con proveedor LLM
### 6.1. Configuración recomendada: Azure OpenAI
- Crear recurso en Azure OpenAI / Azure AI Foundry.
- Configurar endpoint y claves.
- Seleccionar modelo (ej: `gpt-4o-mini`, `gpt-4.1-mini`, etc.).

### 6.2. Implementación en código
- Crear módulo `llm_client.py` o similar.
- Centralizar llamadas al SDK:
  - gestión de errores
  - timeout
  - reintentos
  - logs

### 6.3. Seguridad
- No incluir credenciales en repositorio.
- Usar `.env` y `dotenv`.
- Documentar variables necesarias en `README.md`.

---

## 7. Plan de trabajo (roadmap por fases)

### Fase 1: Preparación del entorno (0.5 días)
- [ ] Configurar entorno virtual
- [ ] Instalar dependencias
- [ ] Configurar variables de entorno
- [ ] Probar conexión básica con el modelo LLM

**Salida esperada:** Script o endpoint mínimo que confirme respuesta del modelo.

---

### Fase 2: Actualización del modelo Task (0.5 días)
- [ ] Añadir campos `category`, `risk_analysis`, `risk_mitigation`
- [ ] Actualizar esquemas de validación (Pydantic / Marshmallow)
- [ ] Ajustar base de datos / migraciones

**Salida esperada:** CRUD funcionando con los nuevos campos.

---

### Fase 3: Endpoint `/ai/tasks/describe` (0.5 días)
- [ ] Implementar endpoint
- [ ] Diseñar prompt para descripción coherente
- [ ] Prueba en Postman

**Salida esperada:** descripción generada correctamente.

---

### Fase 4: Endpoint `/ai/tasks/categorize` (0.5 días)
- [ ] Implementar endpoint
- [ ] Prompt con categorías restringidas
- [ ] Validar respuesta
- [ ] Prueba en Postman

**Salida esperada:** categoría consistente.

---

### Fase 5: Endpoint `/ai/tasks/estimate` (1 día)
- [ ] Implementar endpoint
- [ ] Prompt con salida numérica controlada
- [ ] Parsing seguro del resultado
- [ ] Pruebas de casos límite

**Salida esperada:** esfuerzo en horas válido y numérico.

---

### Fase 6: Endpoint `/ai/tasks/audit` (1 día)
- [ ] Implementar endpoint
- [ ] Primera llamada: análisis de riesgos
- [ ] Segunda llamada: mitigación
- [ ] Pruebas con tareas reales

**Salida esperada:** análisis y mitigación coherentes.

---

### Fase 7: Pruebas finales + documentación (0.5 días)
- [ ] Probar todos los endpoints con Postman / Swagger
- [ ] Añadir ejemplos de payload en README
- [ ] Revisar consistencia de respuestas JSON
- [ ] Validar que el CRUD sigue funcionando

**Salida esperada:** API completa lista para entrega.

---

## 8. Plan de pruebas (Postman / Swagger)

### 8.1. Casos mínimos
- [ ] Crear Task normal (CRUD)
- [ ] Ejecutar `/describe` con description vacía
- [ ] Ejecutar `/categorize` con category vacía
- [ ] Ejecutar `/estimate` con effort_hours vacío
- [ ] Ejecutar `/audit` con risk_analysis y risk_mitigation vacíos
- [ ] Confirmar que cada endpoint devuelve JSON válido

### 8.2. Casos límite recomendados
- [ ] Task sin title (validación debe fallar)
- [ ] Respuesta LLM inválida (manejo de errores)
- [ ] effort_hours devuelto como texto (parsing debe controlarlo)
- [ ] category fuera del listado permitido

---

## 9. Gestión de riesgos técnicos
| Riesgo | Impacto | Mitigación |
|-------|---------|------------|
| Respuestas no controladas del LLM | Alto | Forzar JSON / formato estricto en prompts |
| Parsing incorrecto de horas | Medio | Validar con regex / casting seguro |
| Latencia del modelo | Medio | Implementar timeout y logs |
| Errores de autenticación Azure | Alto | Validar configuración con script inicial |
| Costes por llamadas excesivas | Medio | Limitar tokens y reutilizar prompts |

---

## 10. Criterios de aceptación (rúbrica)
- [ ] `/ai/tasks/describe` implementado correctamente (25%)
- [ ] `/ai/tasks/categorize` implementado correctamente (25%)
- [ ] `/ai/tasks/estimate` implementado correctamente (25%)
- [ ] `/ai/tasks/audit` implementado correctamente (25%)

**Puntuación total:** 10 puntos

---

## 11. Checklist final antes de entrega
- [ ] Código limpio y ejecutable
- [ ] `.env.example` incluido (sin credenciales reales)
- [ ] Dependencias correctas en `requirements.txt`
- [ ] Endpoints documentados en README
- [ ] Proyecto comprimido en `.zip`
- [ ] (Opcional) colección Postman incluida

---
