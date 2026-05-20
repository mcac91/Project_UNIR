"""Tests para el endpoint /ai/tasks/audit y la lógica de auditoría del controller."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.controllers.tasks_controller import TaskController
from app.main import app
from app.models.task import Priority, Status, Task
from app.services.llm_client import LLMResponseError
from app.services.task_manager import TaskManager


class TestAuditTaskController:
    """Tests del controlador de auditoría de tareas."""

    def test_audit_task_updates_risk_analysis_and_mitigation(self, tmp_path: Path) -> None:
        initial_task = Task(
            id=1,
            title="Auditar CI/CD",
            description="Revisar canalización y despliegues automatizados.",
            priority=Priority.ALTA,
            effort_hours=8.0,
            status=Status.EN_PROGRESO,
            assigned_to="ana",
            category="Infra",
        )

        manager = TaskManager(data_file=tmp_path / "tasks.json")
        manager.save_tasks([initial_task])
        controller = TaskController(manager=manager)

        with patch("app.controllers.tasks_controller.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat_completion.side_effect = [
                "Riesgos técnicos clave: dependencia de terceros, falta de pruebas de integración y posible rotura de despliegues automáticos. Se recomienda monitoreo y revisiones frecuentes.",
                "Mitigación principal: implementar pruebas de integración automatizadas, monitoreo continuo y rollback rápido. Establecer alertas y revisión de cambios antes del despliegue.",
            ]
            mock_llm_class.return_value = mock_llm

            result = controller.audit_task(1)

            assert result.id == 1
            assert result.category == "Infra"
            assert result.risk_analysis is not None
            assert result.risk_mitigation is not None
            assert "Riesgos técnicos clave" in result.risk_analysis
            assert "Mitigación principal" in result.risk_mitigation

    def test_audit_task_retries_when_risk_analysis_too_short(self, tmp_path: Path) -> None:
        initial_task = Task(
            id=2,
            title="Auditar seguridad",
            description="Realizar un análisis de seguridad para el módulo de autenticación.",
            priority=Priority.ALTA,
            effort_hours=6.0,
            status=Status.PENDIENTE,
            assigned_to="luis",
            category="Backend",
        )

        manager = TaskManager(data_file=tmp_path / "tasks.json")
        manager.save_tasks([initial_task])
        controller = TaskController(manager=manager)

        with patch("app.controllers.tasks_controller.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat_completion.side_effect = [
                "Muy corto.",
                "Riesgos importantes: la autenticación podría ser vulnerable a ataques de fuerza bruta y falta de cifrado adecuado.",
                "Mitigación recomendada: añadir límites de intentos, validar contraseñas seguras y cifrar todos los datos sensibles. También aplicar revisiones de seguridad periódicas.",
            ]
            mock_llm_class.return_value = mock_llm

            result = controller.audit_task(2)

            assert result.risk_analysis.startswith("Riesgos importantes")
            assert result.risk_mitigation.startswith("Mitigación recomendada")
            assert mock_llm.chat_completion.call_count == 3

    def test_audit_task_raises_value_error_for_missing_required_fields(self, tmp_path: Path) -> None:
        invalid_task = Task(
            id=3,
            title="Auditar",
            description="Short description",
            priority=Priority.BAJA,
            effort_hours=0.0,
            status=Status.PENDIENTE,
            assigned_to="maria",
            category="",
        )

        manager = TaskManager(data_file=tmp_path / "tasks.json")
        manager.save_tasks([invalid_task])
        controller = TaskController(manager=manager)

        with pytest.raises(ValueError, match="auditar"):
            controller.audit_task(3)


class TestAuditTaskEndpoint:
    """Tests del endpoint POST /ai/tasks/audit."""

    def test_audit_task_endpoint_returns_200(self) -> None:
        client = TestClient(app)
        task = Task(
            id=1,
            title="Auditar documentación",
            description="Verificar que la documentación del API esté actualizada.",
            priority=Priority.MEDIA,
            effort_hours=2.0,
            status=Status.PENDIENTE,
            assigned_to="carla",
            category="Docs",
        )

        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.audit_task.return_value = task

            response = client.post("/ai/tasks/1/audit")

            assert response.status_code == 200
            body = response.json()
            assert body["id"] == 1
            assert body["title"] == "Auditar documentación"
            mock_controller.audit_task.assert_called_once_with(1)

    def test_audit_task_endpoint_returns_404_when_task_invalid(self) -> None:
        client = TestClient(app)

        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.audit_task.side_effect = ValueError("Tarea inválida para auditar")

            response = client.post("/ai/tasks/1/audit")

            assert response.status_code == 404
            assert response.json()["detail"] == "Tarea inválida para auditar"

    def test_audit_task_endpoint_returns_502_on_llm_error(self) -> None:
        client = TestClient(app)

        with patch("app.routes.ai_tasks.controller") as mock_controller:
            mock_controller.audit_task.side_effect = LLMResponseError("Error en LLM")

            response = client.post("/ai/tasks/1/audit")

            assert response.status_code == 502
            assert response.json()["detail"] == "Error en LLM"
