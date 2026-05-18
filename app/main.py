import logging
from fastapi import FastAPI

from app.routes.ai_tasks import router as ai_tasks_router
from app.routes.tasks import router as tasks_router

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Gestor de Tareas API",
    description="API REST para gestión de tareas asignadas a usuarios",
    version="1.0.0"
)

app.include_router(tasks_router)
app.include_router(ai_tasks_router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Gestor de Tareas"}