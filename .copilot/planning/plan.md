# Planificación Técnica - Proyecto Gestor de Tareas (Entregable 1)

## 1. Descripción General

Este proyecto consiste en una aplicación de **gestión de tareas asignadas a usuarios**.  
El objetivo del **Entregable 1** es construir la base del proyecto, creando la arquitectura inicial y la lógica principal, que servirá como punto de partida para futuros módulos y ampliaciones.

La aplicación debe exponer una API REST que permita gestionar tareas mediante operaciones CRUD, persistiendo los datos en un fichero JSON.

---

## 2. Justificación Técnica: Sustitución de Flask por FastAPI

Aunque el documento original especifica el uso de Flask, se utilizará **FastAPI** como framework backend por motivos técnicos orientados a mantener el proyecto escalable y fácilmente ampliable en futuros módulos.

### Motivos principales del cambio

- **Validación automática de datos**: FastAPI utiliza Pydantic para validar estructuras de entrada/salida de forma automática.
- **Tipado fuerte y mantenibilidad**: el tipado facilita el crecimiento del proyecto y reduce errores.
- **Documentación automática**: generación inmediata de Swagger/OpenAPI, lo cual mejora el testing y el mantenimiento.
- **Arquitectura moderna y modular**: FastAPI facilita la separación de rutas, controladores y lógica de negocio.

Este cambio no altera el alcance del entregable, solo mejora la base tecnológica sobre la que se construirá el proyecto.

---

## 3. Objetivo del Entregable 1

Desarrollar una API REST funcional que permita gestionar tareas de usuario, incluyendo:

- Arquitectura base del proyecto
- Implementación de la entidad `Task`
- Implementación de la lógica de persistencia en JSON mediante `TaskManager`
- Exposición de endpoints CRUD con respuestas en formato JSON

---

## 4. Requisitos Funcionales

### 4.1 Modelo de Datos: Task

La aplicación debe gestionar tareas con los siguientes campos:

- `id` (primary key)
- `title` (título de la tarea)
- `description` (texto largo)
- `priority` (baja, media, alta, bloqueante)
- `effort_hours` (número decimal, horas estimadas)
- `status` (pendiente, en progreso, en revisión, completada)
- `assigned_to` (persona del equipo asignada)

---

## 5. Endpoints Requeridos

Se deben implementar los siguientes endpoints:

- **POST** `/tasks` → Crear una tarea
- **GET** `/tasks` → Leer todas las tareas
- **GET** `/tasks/{id}` → Leer una tarea específica
- **PUT** `/tasks/{id}` → Actualizar una tarea
- **DELETE** `/tasks/{id}` → Eliminar una tarea

Las respuestas deben devolverse en formato JSON.

---

## 6. Persistencia de Datos

La persistencia de tareas se realizará mediante un fichero JSON local:

- Archivo: `tasks.json`

Este archivo actuará como base de datos inicial del sistema.

---

## 7. Componentes Obligatorios del Proyecto

El proyecto debe incluir los siguientes elementos:

- Entorno virtual configurado (`venv`)
- Instalación de librerías necesarias
- Fichero `requirements.txt`
- Arquitectura organizada en ficheros/carpetas
- Fichero de rutas que registre los endpoints
- Controladores conectados con la lógica del sistema
- Clases `Task` y `TaskManager`

---

## 8. Diseño de Clases

### 8.1 Clase `Task`

Representa una tarea con la estructura definida.

**Métodos requeridos:** 

- `to_dict()` → Convierte el objeto Task a diccionario.
- `from_dict()` → Crea un objeto Task a partir de un diccionario.

---

### 8.2 Clase `TaskManager`

Clase responsable de la carga y guardado de tareas desde el fichero JSON.

**Métodos estáticos requeridos:**

- `load_tasks()` → Carga tareas desde `tasks.json` y las convierte en objetos Task.
- `save_tasks()` → Guarda la lista de objetos Task en el archivo JSON.

---

## 9. Arquitectura Recomendada del Proyecto

El documento requiere una arquitectura organizada y modular.  
La estructura recomendada (adaptada a FastAPI) debe facilitar la incorporación de futuras capas sin reestructurar el código base.

Ejemplo recomendado:
project/
│
├── app/
│ ├── main.py
│ ├── routes/
│ │ └── tasks.py
│ ├── controllers/
│ │ └── tasks_controller.py
│ ├── models/
│ │ └── task.py
│ ├── services/
│ │ └── task_manager.py
│ └── data/
│ └── tasks.json
│
├── requirements.txt
└── README.md

**Notas:**
- `routes/` define endpoints.
- `controllers/` implementa lógica de petición/respuesta.
- `services/` contiene lógica de persistencia.
- `models/` define la entidad Task.

---

## 10. Plan de Trabajo (Entregable 1)

### Paso 1: Preparación del entorno
- Crear entorno virtual
- Instalar dependencias
- Generar `requirements.txt`

### Paso 2: Crear arquitectura del proyecto
- Crear carpetas base (`routes`, `controllers`, `models`, `services`, `data`)
- Configurar punto de entrada (`main.py`)

### Paso 3: Implementar modelo `Task`
- Definir atributos del modelo
- Implementar `to_dict()` y `from_dict()`

### Paso 4: Implementar `TaskManager`
- Implementar `load_tasks()`
- Implementar `save_tasks()`
- Asegurar lectura/escritura correcta en `tasks.json`

### Paso 5: Implementar endpoints CRUD
- Crear fichero de rutas
- Conectar rutas con controlador
- Conectar controlador con TaskManager

### Paso 6: Validación final
- Probar todos los endpoints
- Verificar persistencia correcta en JSON
- Comprobar formato correcto de respuestas

---

## 11. Consideración Importante: Evolución por Capas Futuras

El documento indica que este entregable es solo el inicio y que el proyecto será reutilizado en módulos posteriores.

Por lo tanto, el diseño debe cumplir:

- Separación clara de responsabilidades (rutas, controladores, servicios, modelos)
- Código mantenible y modular
- Facilidad para añadir nuevas capas (persistencia avanzada, autenticación, validaciones adicionales, etc.)

⚠️ No se definen aún las futuras capas, por lo que este entregable debe centrarse en crear una base limpia y extensible.

---

## 12. Formato de Entrega

El proyecto debe entregarse en un archivo comprimido con el formato:

`m2_proyecto_nombre_apellido.zip`

Incluyendo dentro:
- carpeta con el proyecto
- código fuente Python
- fichero `requirements.txt`
- estructura completa y funcional

---

## 13. Criterios de Evaluación (Rúbrica)

El entregable será evaluado según los siguientes puntos: 

- Arquitectura del proyecto: **25%**
- Clase Task: **25%**
- Clase TaskManager: **25%**
- Creación de rutas/endpoints: **25%**

Puntuación total: **10 puntos (100%)**