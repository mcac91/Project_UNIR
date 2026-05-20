"""Tests para el endpoint /ai/tasks/estimate."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.controllers.tasks_controller import TaskController, parse_effort_response
from app.main import app
from app.models.task import Priority, Status, Task
from app.services.task_manager import TaskManager


class TestParseEffortResponse:
    """Tests para la función parse_effort_response."""

    def test_parse_valid_json(self) -> None:
        """Test parsear JSON válido con horas en rango."""
        response = '{"hours": 5.5}'
        assert parse_effort_response(response) == 5.5

    def test_parse_valid_json_integer(self) -> None:
        """Test parsear JSON válido con número entero."""
        response = '{"hours": 8}'
        assert parse_effort_response(response) == 8.0

    def test_parse_text_with_hours(self) -> None:
        """Test parsear texto con palabra 'horas'."""
        response = "Estimo 8 horas para esta tarea"
        assert parse_effort_response(response) == 8.0

    def test_parse_text_with_hora_singular(self) -> None:
        """Test parsear texto con palabra 'hora' singular."""
        response = "Esto toma 1 hora aproximadamente"
        assert parse_effort_response(response) == 1.0

    def test_parse_first_number_in_text(self) -> None:
        """Test parsear primer número encontrado."""
        response = "Aproximadamente 12 horas de trabajo"
        assert parse_effort_response(response) == 12.0

    def test_parse_decimal_number(self) -> None:
        """Test parsear número decimal."""
        response = "Se estima 3.5 horas"
        assert parse_effort_response(response) == 3.5

    def test_parse_empty_response_raises_error(self) -> None:
        """Test que respuesta vacía lanza ValueError."""
        with pytest.raises(ValueError, match="vacía"):
            parse_effort_response("")

    def test_parse_whitespace_only_raises_error(self) -> None:
        """Test que respuesta solo espacios lanza ValueError."""
        with pytest.raises(ValueError, match="vacía"):
            parse_effort_response("   ")

    def test_parse_no_numbers_raises_error(self) -> None:
        """Test que respuesta sin números lanza ValueError."""
        with pytest.raises(ValueError, match="No se pudo extraer"):
            parse_effort_response("No hay números aquí")

    def test_parse_number_below_minimum_raises_error(self) -> None:
        """Test que número menor a 0.5 lanza ValueError."""
        with pytest.raises(ValueError, match="No se pudo extraer"):
            parse_effort_response('{"hours": 0.2}')

    def test_parse_number_above_maximum_raises_error(self) -> None:
        """Test que número mayor a 80 lanza ValueError."""
        with pytest.raises(ValueError, match="No se pudo extraer"):
            parse_effort_response('{"hours": 200}')

    def test_parse_minimum_valid_hours(self) -> None:
        """Test que 0.5 horas (mínimo) es válido."""
        assert parse_effort_response('{"hours": 0.5}') == 0.5

    def test_parse_maximum_valid_hours(self) -> None:
        """Test que 80 horas (máximo) es válido."""
        assert parse_effort_response('{"hours": 80}') == 80.0

    def test_parse_malformed_json_fallback_to_regex(self) -> None:
        """Test que JSON malformado fallback a regex."""
        response = '{"hours": 6 horas'  # JSON inválido pero contiene 6
        # Debería encontrar el 6 con regex
        assert parse_effort_response(response) == 6.0

    def test_parse_json_without_hours_key(self) -> None:
        """Test que JSON sin key 'hours' fallback a búsqueda de número."""
        response = '{"effort": 5}'
        # Debería fallar JSON, luego regex, luego buscar números
        assert parse_effort_response(response) == 5.0


class TestEstimateEffortEndpoint:
    """Tests para el endpoint POST /ai/tasks/estimate."""

    def test_estimate_effort_updates_hours_successfully(
        self, tmp_path: Path
    ) -> None:
        """Test que endpoint actualiza effort_hours correctamente."""
        client = TestClient(app)
        tasks_file = tmp_path / "tasks.json"

        # Crear tarea inicial
        initial_task = Task(
            id=1,
            title="Crear API REST",
            description="Implementar endpoints de tareas",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="juan",
        )

        # Mock del controller y del cliente LLM
        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.estimate_effort.return_value = initial_task

            response = client.post("/ai/tasks/1/estimate")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["title"] == "Crear API REST"
            mock_controller.estimate_effort.assert_called_once_with(1)

    def test_estimate_effort_task_not_found(self) -> None:
        """Test que tarea inexistente retorna 404."""
        client = TestClient(app)

        with patch("app.controllers.tasks_controller.TaskManager") as mock_manager_class:
            mock_manager_instance = MagicMock()
            mock_manager_instance.get_task.side_effect = ValueError(
                "Tarea con id 999 no encontrada"
            )
            mock_manager_class.return_value = mock_manager_instance

            response = client.post("/ai/tasks/999/estimate")

            assert response.status_code == 404

    def test_estimate_effort_missing_title_returns_404(self) -> None:
        """Test que tarea sin title retorna 404."""
        client = TestClient(app)

        task_without_title = MagicMock()
        task_without_title.title = ""
        task_without_title.description = "Descripción"
        task_without_title.priority = Priority.MEDIA
        task_without_title.effort_hours = 0
        task_without_title.status = Status.PENDIENTE
        task_without_title.assigned_to = "juan"
        task_without_title.category = "Backend"
        task_without_title.risk_analysis = None
        task_without_title.risk_mitigation = None

        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.estimate_effort.side_effect = ValueError(
                "Tarea debe tener title y description para estimar esfuerzo"
            )

            response = client.post("/ai/tasks/1/estimate")

            assert response.status_code == 404

    def test_estimate_effort_missing_description_returns_404(self) -> None:
        """Test que tarea sin description retorna 404."""
        client = TestClient(app)

        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.estimate_effort.side_effect = ValueError(
                "Tarea debe tener title y description para estimar esfuerzo"
            )

            response = client.post("/ai/tasks/1/estimate")

            assert response.status_code == 404

    def test_estimate_effort_llm_error_returns_502(self) -> None:
        """Test que error LLM retorna 502."""
        client = TestClient(app)

        task = Task(
            id=1,
            title="Crear API",
            description="Implementar endpoints",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="juan",
        )

        with patch("app.controllers.tasks_controller.TaskManager") as mock_manager_class:
            with patch(
                "app.controllers.tasks_controller.LLMClient"
            ) as mock_llm_client_class:
                mock_manager_instance = MagicMock()
                mock_manager_instance.get_task.return_value = task
                mock_manager_class.return_value = mock_manager_instance

                from app.services.llm_client import LLMResponseError

                mock_llm_instance = MagicMock()
                mock_llm_instance.chat_completion.side_effect = LLMResponseError(
                    "LLM error"
                )
                mock_llm_client_class.return_value = mock_llm_instance

                response = client.post("/ai/tasks/1/estimate")

                assert response.status_code == 502

    def test_estimate_effort_timeout_returns_504(self) -> None:
        """Test que timeout LLM retorna 504."""
        client = TestClient(app)

        task = Task(
            id=1,
            title="Crear API",
            description="Implementar endpoints",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="juan",
        )

        with patch("app.controllers.tasks_controller.TaskManager") as mock_manager_class:
            with patch(
                "app.controllers.tasks_controller.LLMClient"
            ) as mock_llm_client_class:
                mock_manager_instance = MagicMock()
                mock_manager_instance.get_task.return_value = task
                mock_manager_class.return_value = mock_manager_instance

                from app.services.llm_client import LLMTimeoutError

                mock_llm_instance = MagicMock()
                mock_llm_instance.chat_completion.side_effect = LLMTimeoutError(
                    "Timeout"
                )
                mock_llm_client_class.return_value = mock_llm_instance

                response = client.post("/ai/tasks/1/estimate")

                assert response.status_code == 504

    def test_estimate_effort_connection_error_returns_503(self) -> None:
        """Test que error conexión LLM retorna 503."""
        client = TestClient(app)

        task = Task(
            id=1,
            title="Crear API",
            description="Implementar endpoints",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="juan",
        )

        with patch("app.controllers.tasks_controller.TaskManager") as mock_manager_class:
            with patch(
                "app.controllers.tasks_controller.LLMClient"
            ) as mock_llm_client_class:
                mock_manager_instance = MagicMock()
                mock_manager_instance.get_task.return_value = task
                mock_manager_class.return_value = mock_manager_instance

                from app.services.llm_client import LLMConnectionError

                mock_llm_instance = MagicMock()
                mock_llm_instance.chat_completion.side_effect = LLMConnectionError(
                    "Connection error"
                )
                mock_llm_client_class.return_value = mock_llm_instance

                response = client.post("/ai/tasks/1/estimate")

                assert response.status_code == 503


class TestEstimateEffortController:
    """Tests para el método estimate_effort del controller."""

    def test_controller_estimate_effort_returns_updated_task(self, tmp_path: Path) -> None:
        """Test que controller actualiza task con horas estimadas."""
        tasks_file = tmp_path / "tasks.json"

        initial_task = Task(
            id=1,
            title="API Task",
            description="Build REST API",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="juan",
            category="Backend",
        )

        manager = TaskManager(data_file=tasks_file)
        manager.save_tasks([initial_task])

        controller = TaskController(manager=manager)

        with patch("app.controllers.tasks_controller.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat_completion.return_value = '{"hours": 6.0}'
            mock_llm_class.return_value = mock_llm

            result = controller.estimate_effort(1)

            assert result.id == 1
            assert result.effort_hours == 6.0
            assert result.title == "API Task"

    def test_controller_estimate_effort_with_regex_fallback(
        self, tmp_path: Path
    ) -> None:
        """Test que controller maneja respuesta con regex fallback."""
        tasks_file = tmp_path / "tasks.json"

        initial_task = Task(
            id=1,
            title="Testing Task",
            description="Write unit tests",
            priority=Priority.MEDIA,
            effort_hours=0,
            status=Status.PENDIENTE,
            assigned_to="maria",
            category="Testing",
        )

        manager = TaskManager(data_file=tasks_file)
        manager.save_tasks([initial_task])

        controller = TaskController(manager=manager)

        with patch("app.controllers.tasks_controller.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            # Simular respuesta con texto
            mock_llm.chat_completion.return_value = "Aproximadamente 4 horas"
            mock_llm_class.return_value = mock_llm

            result = controller.estimate_effort(1)

            assert result.effort_hours == 4.0

    def test_controller_estimate_effort_preserves_other_fields(
        self, tmp_path: Path
    ) -> None:
        """Test que controller preserva otros campos de la tarea."""
        tasks_file = tmp_path / "tasks.json"

        initial_task = Task(
            id=2,
            title="Infra Task",
            description="Setup CI/CD",
            priority=Priority.ALTA,
            effort_hours=0,
            status=Status.EN_PROGRESO,
            assigned_to="carlos",
            category="Infra",
            risk_analysis="Posible caída de servicio",
        )

        manager = TaskManager(data_file=tasks_file)
        manager.save_tasks([initial_task])

        controller = TaskController(manager=manager)

        with patch("app.controllers.tasks_controller.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat_completion.return_value = '{"hours": 16.0}'
            mock_llm_class.return_value = mock_llm

            result = controller.estimate_effort(2)

            assert result.title == "Infra Task"
            assert result.priority == Priority.ALTA
            assert result.status == Status.EN_PROGRESO
            assert result.assigned_to == "carlos"
            assert result.risk_analysis == "Posible caída de servicio"
            assert result.effort_hours == 16.0
