from fastapi.testclient import TestClient

from app.main import app
from app.models.task import Priority, Status, Task
from app.controllers.tasks_controller import TaskController
from app.services.task_manager import TaskManager
from app.config.constants import TASK_CATEGORIES


def test_categorize_task_endpoint_assigns_valid_category(monkeypatch, tmp_path) -> None:
    """Test que endpoint categorize asigna categoría válida."""
    class FakeManager:
        def __init__(self):
            self.tasks_file = tmp_path / "tasks.json"
            self.real_manager = TaskManager(data_file=self.tasks_file)
            # Crear tarea inicial
            task = Task(
                id=1,
                title="Crear API REST",
                description="Implementar endpoints",
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

    # Mock LLMClient para que retorne categoría válida
    class FakeLLMClient:
        def chat_completion(self, messages, temperature=0.3, max_completion_tokens=50):
            return "Backend"

    monkeypatch.setattr("app.controllers.tasks_controller.LLMClient", lambda *args, **kwargs: FakeLLMClient())
    monkeypatch.setattr("app.routes.ai_tasks.controller", fake_controller)

    client = TestClient(app)
    response = client.post("/ai/tasks/1/categorize")

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Backend"
    assert data["id"] == 1
    assert data["title"] == "Crear API REST"


def test_categorize_task_endpoint_returns_404_for_nonexistent_task() -> None:
    """Test que endpoint retorna 404 si tarea no existe."""
    client = TestClient(app)
    response = client.post("/ai/tasks/9999/categorize")

    assert response.status_code == 404


def test_categorize_task_defaults_to_other_for_invalid_category(monkeypatch, tmp_path) -> None:
    """Test que endpoint asigna 'Other' si categoría es inválida."""
    class FakeManager:
        def __init__(self):
            self.tasks_file = tmp_path / "tasks.json"
            self.real_manager = TaskManager(data_file=self.tasks_file)
            # Crear tarea inicial
            task = Task(
                id=1,
                title="Tarea de prueba",
                description="Descripción",
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

    # Mock LLMClient para retornar categoría inválida
    class FakeLLMClient:
        def chat_completion(self, messages, temperature=0.3, max_completion_tokens=50):
            return "InvalidCategory"

    monkeypatch.setattr("app.controllers.tasks_controller.LLMClient", lambda *args, **kwargs: FakeLLMClient())
    monkeypatch.setattr("app.routes.ai_tasks.controller", fake_controller)

    client = TestClient(app)
    response = client.post("/ai/tasks/1/categorize")

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Other"  # Categoría por defecto


def test_controller_categorize_task_calls_llm_client(monkeypatch, tmp_path) -> None:
    """Test que controller categorize llama a LLM con prompts correctos."""
    class FakeLLMClient:
        def chat_completion(self, messages, temperature=0.3, max_completion_tokens=50):
            # Verificar que el prompt contiene las categorías
            assert any("Frontend" in message["content"] for message in messages)
            assert any("Backend" in message["content"] for message in messages)
            return "Frontend"

    monkeypatch.setattr("app.controllers.tasks_controller.LLMClient", lambda *args, **kwargs: FakeLLMClient())

    manager = TaskManager(data_file=tmp_path / "tasks.json")
    # Crear tarea de prueba
    task = Task(
        id=1,
        title="Crear interfaz",
        description="Interfaz de usuario",
        priority=Priority.MEDIA,
        effort_hours=5.0,
        status=Status.PENDIENTE,
        assigned_to="juan",
    )
    manager.save_tasks([task])

    controller = TaskController(manager=manager)
    result = controller.categorize_task(1)

    assert result.category == "Frontend"
    assert result.title == "Crear interfaz"


def test_categorize_task_all_valid_categories(monkeypatch, tmp_path) -> None:
    """Test que todas las categorías válidas se aceptan sin convertirse a 'Other'."""
    class FakeManager:
        def __init__(self):
            self.tasks_file = tmp_path / "tasks.json"
            self.real_manager = TaskManager(data_file=self.tasks_file)

        def get_task(self, task_id: int):
            return self.real_manager.get_task(task_id)

        def update_task(self, task: Task):
            return self.real_manager.update_task(task)

    manager = FakeManager()
    controller = TaskController(manager=manager.real_manager)

    for category in TASK_CATEGORIES:
        # Crear tarea para cada categoría
        task = Task(
            id=1,
            title=f"Tarea {category}",
            description="Descripción",
            priority=Priority.MEDIA,
            effort_hours=5.0,
            status=Status.PENDIENTE,
            assigned_to="juan",
        )
        manager.real_manager.save_tasks([task])

        # Mock LLMClient retornando la categoría actual
        class FakeLLMClient:
            def __init__(self, current_category):
                self.current_category = current_category

            def chat_completion(self, messages, temperature=0.3, max_completion_tokens=50):
                return self.current_category

        fake_llm = FakeLLMClient(category)
        monkeypatch.setattr(
            "app.controllers.tasks_controller.LLMClient",
            lambda *args, **kwargs: fake_llm,
        )

        result = controller.categorize_task(1)
        assert result.category == category
