from fastapi import FastAPI

app = FastAPI(
    title="Gestor de Tareas API",
    description="API REST para gestión de tareas asignadas a usuarios",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Gestor de Tareas"}