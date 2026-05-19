from fastapi.testclient import TestClient

from app.main import app
from app.models.task import Priority, Status, Task
from app.controllers.tasks_controller import TaskController
from app.services.task_manager import TaskManager


def test_describe_task_endpoint_generates_and_updates_task(monkeypatch, tmp_path) -> None:
    class FakeManager:
        def __init__(self):
            self.tasks_file = tmp_path / "tasks.json"
            self.real_manager = TaskManager(data_file=self.tasks_file)
            # Crear tarea inicial
            task = Task(
                id=1,
                title="Implementar API",
                description="API REST inicial",
                priority=Priority.MEDIA,
                effort_hours=5.0,
                status=Status.PENDIENTE,
                assigned_to="juan",
            )
            self.real_manager.save_tasks([task])

        def get_task(self, task_id: int):
            return self.real_manager.get_task(task_id)

        def update_task(self, task: Task):
            return self.real_manager.update_task(task)

    fake_manager = FakeManager()
    fake_controller = TaskController(manager=fake_manager)

    # Mock LLMClient para que retorne descripción generada
    class FakeLLMClient:
        def chat_completion(self, messages, temperature=0.5, max_completion_tokens=200):
            return "Descripción generada para: Implementar API"

    monkeypatch.setattr("app.controllers.tasks_controller.LLMClient", lambda *args, **kwargs: FakeLLMClient())
    monkeypatch.setattr("app.routes.ai_tasks.controller", fake_controller)

    client = TestClient(app)
    response = client.post("/ai/tasks/1/describe")

    assert response.status_code == 200
    data = response.json()
    assert "Descripción generada para:" in data["description"]
    assert data["id"] == 1
    assert data["title"] == "Implementar API"


def test_describe_task_endpoint_returns_404_for_nonexistent_task() -> None:
    client = TestClient(app)
    response = client.post("/ai/tasks/9999/describe")

    assert response.status_code == 404


def test_controller_describe_task_calls_llm_client(monkeypatch, tmp_path) -> None:
    class FakeLLMClient:
        def chat_completion(self, messages, temperature=0.5, max_completion_tokens=200):
            assert any("Describe" in message["content"] for message in messages)
            return "Descripción de prueba."

    monkeypatch.setattr("app.controllers.tasks_controller.LLMClient", lambda *args, **kwargs: FakeLLMClient())

    manager = TaskManager(data_file=tmp_path / "tasks.json")
    # Crear tarea de prueba
    task = Task(
        id=1,
        title="Probar AI",
        description="Detalle de prueba",
        priority=Priority.MEDIA,
        effort_hours=5.0,
        status=Status.PENDIENTE,
        assigned_to="juan",
    )
    manager.save_tasks([task])

    controller = TaskController(manager=manager)
    result = controller.describe_task(1)

    assert result.description == "Descripción de prueba."
    assert result.title == "Probar AI"

