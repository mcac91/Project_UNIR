from app.models.task import Priority, Status, Task, TaskCreate


def test_task_create_includes_new_optional_fields() -> None:
    task_create = TaskCreate(
        title="Implementar nueva funcionalidad",
        description="Descripción de la tarea.",
        priority=Priority.MEDIA,
        effort_hours=4.5,
        status=Status.PENDIENTE,
        assigned_to="juan",
    )

    assert task_create.category == ""
    assert task_create.risk_analysis is None
    assert task_create.risk_mitigation is None

    task = Task(id=1, **task_create.model_dump())
    assert task.id == 1
    assert task.category == ""
    assert task.risk_analysis is None
    assert task.risk_mitigation is None


def test_task_model_accepts_category_and_risk_fields() -> None:
    task = Task(
        id=2,
        title="Revisar documentación",
        description="Generar la documentación del API.",
        priority=Priority.ALTA,
        effort_hours=2.0,
        status=Status.EN_PROGRESO,
        assigned_to="maria",
        category="Docs",
        risk_analysis="Existe riesgo de falta de información.",
        risk_mitigation="Programar revisiones y validaciones con el equipo.",
    )

    assert task.category == "Docs"
    assert task.risk_analysis == "Existe riesgo de falta de información."
    assert task.risk_mitigation == "Programar revisiones y validaciones con el equipo."


def test_task_serialization_preserves_optional_fields() -> None:
    task = Task(
        id=3,
        title="Crear casos de prueba",
        description="Escribir tests unitarios para el modelo Task.",
        priority=Priority.MEDIA,
        effort_hours=3.0,
        status=Status.PENDIENTE,
        assigned_to="ana",
        category="Testing",
    )

    data = task.to_dict()
    assert data["category"] == "Testing"
    assert data["risk_analysis"] is None
    assert data["risk_mitigation"] is None

    restored = Task.from_dict(data)
    assert restored.category == "Testing"
    assert restored.risk_analysis is None
    assert restored.risk_mitigation is None
