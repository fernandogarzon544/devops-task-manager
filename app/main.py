"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import tasks


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Crea las tablas al iniciar y libera conexiones al detener."""
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="DevOps Task Manager API",
    description="API REST de gestión de tareas — Proyecto Integrador DevOps",
    version="1.1.1",
)

app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Endpoint de salud usado por liveness y readiness probes de Kubernetes."""
    return {"status": "ok"}
