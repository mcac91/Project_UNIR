from fastapi.testclient import TestClient

from app.main import app
from app.models.task import Priority, Status
from app.services.task_manager import TaskManager


def test_describe_task_endpoint_generates_and_updates_task(monkeypatch, tmp_path) -> None:
    from app.models.task import Task

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

        def describe_task(self, title: str, context: str | None = None):
            return f"Descripción generada para: {title}"

        def update_task_description(self, task_id: int, description: str):
            return self.real_manager.update_task_description(task_id, description)

    fake_manager = FakeManager()
    monkeypatch.setattr("app.routes.ai_tasks.manager", fake_manager)

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


def test_task_manager_describe_task_calls_llm_client(monkeypatch, tmp_path) -> None:
    class FakeClient:
        def chat_completion(self, messages, temperature=0.5, max_completion_tokens=200):
            # No especifica model: LLMClient debería usar su default_model
            assert any("Describe" in message["content"] for message in messages)
            return "Descripción de prueba."

    monkeypatch.setattr("app.services.task_manager.LLMClient", lambda *args, **kwargs: FakeClient())

    from app.services.task_manager import TaskManager

    manager = TaskManager(data_file=tmp_path / "tasks.json")
    description = manager.describe_task("Probar AI", context="Detalle de prueba")

    assert description == "Descripción de prueba."
