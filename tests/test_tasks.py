"""Once pruebas de integración con SQLite en memoria."""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Entrega sesiones del motor en memoria."""
    with TestingSessionLocal() as db:
        yield db


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    """Aísla las tablas y restaura las dependencias al terminar cada prueba."""
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


client = TestClient(app)


def test_health_check() -> None:
    """Comprueba el endpoint de salud."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task() -> None:
    """Crea una tarea con descripción y rechaza un título omitido."""
    response = client.post("/tasks/", json={"title": "Estudiar", "description": "Unidad 1"})
    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "title": "Estudiar", "description": "Unidad 1", "completed": False
    }
    assert client.post("/tasks/", json={"description": "Sin título"}).status_code == 422


def test_create_task_sin_descripcion() -> None:
    """Permite crear tareas sin descripción."""
    response = client.post("/tasks/", json={"title": "Leer"})
    assert response.status_code == 201
    assert response.json()["description"] is None
    assert response.json()["completed"] is False


def test_listar_tareas_vacia() -> None:
    """Devuelve una lista vacía al iniciar."""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_tareas() -> None:
    """Devuelve todas las tareas creadas."""
    client.post("/tasks/", json={"title": "Primera"})
    client.post("/tasks/", json={"title": "Segunda"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert {task["title"] for task in response.json()} == {"Primera", "Segunda"}


def test_get_task_existente() -> None:
    """Consulta por el ID que devuelve la creación."""
    task = client.post("/tasks/", json={"title": "Consultar"}).json()
    response = client.get(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json() == task


def test_get_task_no_existente() -> None:
    """Devuelve 404 al consultar una tarea ausente."""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tarea no encontrada"


def test_update_task() -> None:
    """Actualiza parcialmente y conserva los campos omitidos."""
    task = client.post("/tasks/", json={"title": "Original", "description": "Conservar"}).json()
    response = client.put(f"/tasks/{task['id']}", json={"completed": True})
    assert response.status_code == 200
    assert response.json() == {**task, "completed": True}
    edited = client.put(f"/tasks/{task['id']}", json={"title": "Editada", "description": None})
    assert edited.status_code == 200
    assert edited.json()["title"] == "Editada"
    assert edited.json()["description"] is None
    assert edited.json()["completed"] is True


def test_update_task_no_existente() -> None:
    """Devuelve 404 al editar una tarea ausente."""
    assert client.put("/tasks/999", json={"completed": True}).status_code == 404


def test_eliminar_tarea() -> None:
    """Elimina sin cuerpo y comprueba que la tarea desaparece."""
    task = client.post("/tasks/", json={"title": "Eliminar"}).json()
    response = client.delete(f"/tasks/{task['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/tasks/{task['id']}").status_code == 404
    assert client.get("/tasks/").json() == []


def test_eliminar_tarea_no_existente() -> None:
    """Devuelve 404 al eliminar una tarea ausente."""
    assert client.delete("/tasks/999").status_code == 404
