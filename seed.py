"""Puebla SQLite con diez tareas iniciales del proyecto."""
import argparse

from sqlalchemy import delete

from app.database import Base, SessionLocal, TaskDB, engine

TASKS = [
    {"title": title, "description": description, "completed": completed}
    for title, description, completed in [
        ("Crear estructura FastAPI", "Organizar los módulos de la API", True),
        ("Implementar CRUD de tareas", "Crear, consultar, actualizar y eliminar", True),
        ("Tests con pytest", "Verificar once casos con base aislada", True),
        ("Dockerfile multietapa", "Ejecutar la imagen como appuser", True),
        ("Configurar Jenkins", "Preparar el servicio de integración", False),
        ("Automatizar las pruebas", "Ejecutar pytest en el pipeline", False),
        ("Publicar la imagen", "Enviar la imagen al registro", False),
        ("Crear el Deployment", "Desplegar la API en Kubernetes", False),
        ("Configurar el Service", "Exponer las réplicas de la API", False),
        ("Supervisar la aplicación", "Revisar salud y métricas", False),
    ]
]


def seed(force: bool = False) -> None:
    """Inserta las tareas si la base está vacía o reinicia con --force."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        if force:
            db.execute(delete(TaskDB))
        elif db.query(TaskDB).count():
            print("La base ya tiene datos. Usa --force para reiniciarla.")
            return
        db.add_all(TaskDB(**task) for task in TASKS)
    print(f"Seed completado: {len(TASKS)} tareas insertadas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Reemplaza las tareas existentes.")
    seed(force=parser.parse_args().force)
