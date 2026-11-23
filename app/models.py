"""Pydantic schemas for request validation and response serialization."""
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """Datos necesarios para crear una tarea."""
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    """Campos opcionales de una actualización parcial."""
    title:       str  | None = None
    description: str  | None = None
    completed:   bool | None = None


class TaskResponse(BaseModel):
    """Datos públicos de una tarea."""
    id:          int
    title:       str
    description: str | None = None
    completed:   bool

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2: leer desde ORM objects
