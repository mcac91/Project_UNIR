from fastapi.testclient import TestClient

from app.main import app


def test_describe_task_endpoint_returns_generated_description(monkeypatch) -> None:
    class FakeManager:
        def describe_task(self, title: str, context: str | None = None, model: str | None = None) -> str:
            assert title == "Crear endpoint AI"
            assert context == "Generar texto de ejemplo."
            return "Descripción generada por IA."

    monkeypatch.setattr("app.routes.ai_tasks.manager", FakeManager())
    client = TestClient(app)
    response = client.post(
        "/ai/tasks/describe",
        json={"title": "Crear endpoint AI", "description": "Generar texto de ejemplo."},
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Descripción generada por IA."
    assert response.json()["title"] == "Crear endpoint AI"


def test_describe_task_endpoint_requires_title() -> None:
    client = TestClient(app)
    response = client.post("/ai/tasks/describe", json={"description": "Sin título"})

    assert response.status_code == 422


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
