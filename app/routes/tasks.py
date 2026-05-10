from fastapi import APIRouter, HTTPException

from app.controllers.tasks_controller import TaskController
from app.models.task import Task, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])
controller = TaskController()


@router.get("/", response_model=list[Task])
async def read_tasks() -> list[Task]:
    return controller.list_tasks()


@router.get("/{task_id}", response_model=Task)
async def read_task(task_id: int) -> Task:
    try:
        return controller.get_task(task_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskCreate) -> Task:
    try:
        return controller.create_task(task)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskCreate) -> Task:
    try:
        return controller.update_task(task_id, task)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int) -> None:
    try:
        controller.delete_task(task_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
