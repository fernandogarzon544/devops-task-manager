# DevOps Task Manager API

Proyecto integrador de Semana 1. API REST de tareas con FastAPI, SQLite, SQLAlchemy 2.0, Pydantic v2, once pruebas de integración y Docker multietapa.

## Requisitos

Python 3.10 o posterior, Git y Docker Desktop. El proyecto se verificó en macOS con Python 3.12.16. En Windows puedes sustituir el primer comando por `py -3.12 -m venv .venv` y activar con `.venv\Scripts\Activate.ps1`.

## 1. Preparar el entorno

```sh
git clone https://github.com/fernandogarzon544/devops-task-manager.git
cd devops-task-manager
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

Las versiones están fijadas según avance-semana-1. Los módulos de la API están separados en persistencia, esquemas y rutas.

## 2. Comprobar la base y los esquemas

```sh
python -c 'from app.database import TaskDB, get_db; from app.models import TaskCreate, TaskUpdate, TaskResponse; print(TaskDB.__tablename__); print(TaskCreate(title="Revisar").model_dump())'
```

`get_db()` abre una sesión por petición y la cierra al terminar. Los esquemas usan uniones `X | None` y `TaskResponse` lee objetos ORM mediante `ConfigDict(from_attributes=True)`.

## 3. Ejecutar la API local

```sh
python -m uvicorn app.main:app --reload
```

Abre [Swagger UI](http://127.0.0.1:8000/docs) o [salud](http://127.0.0.1:8000/health). Para mantener Docker y la API local encendidos a la vez, agrega `--port 8001` a este comando.

| Método | Ruta | Resultado |
| --- | --- | --- |
| GET | /health | 200, estado de salud |
| GET | /tasks/ | 200, lista |
| POST | /tasks/ | 201, tarea creada |
| GET | /tasks/{task_id} | 200 o 404 |
| PUT | /tasks/{task_id} | 200 o 404 |
| DELETE | /tasks/{task_id} | 204 sin cuerpo o 404 |

Un POST necesita `title` y acepta `description`. Un PUT aplica solo los campos enviados mediante `exclude_unset=True`. Se conserva el comportamiento de la guía para `title: null` en una actualización, que causa un error de integridad porque la columna es obligatoria. Esa validación queda como mejora pendiente.

## 4. Ejecutar las once pruebas

```sh
python -m pytest tests/ -v
```

La suite sigue los once casos enumerados por la guía. Incluye salud, creación con y sin descripción, listado vacío y con datos, consulta, edición, eliminación y tres casos 404. Dentro de creación también comprueba el 422 por título omitido.

Las pruebas usan `sqlite:///:memory:`, `StaticPool` y `app.dependency_overrides`. Cada prueba crea y elimina sus tablas. Las tablas de producción se crean al arrancar la aplicación mediante `lifespan`, para que importar el módulo durante pytest tampoco genere un archivo en disco.

## 5. Construir la imagen

```sh
docker build -t devops-task-api:semana1 .
docker run --rm --entrypoint id devops-task-api:semana1
docker run --rm -p 127.0.0.1:8000:8000 devops-task-api:semana1
```

El Dockerfile usa `python:3.12-slim` en builder y runtime. Copia las dependencias desde `/install` y ejecuta Uvicorn como `appuser`. La base del contenedor queda en `/app/data/tasks.db`.

## 6. Usar Compose con hot-reload

Detén el servidor que esté usando el puerto 8000 y ejecuta:

```sh
docker compose up --build -d
docker compose logs api
docker compose exec api id
```

El montaje `./app:/app/app` permite recargar el código al editarlo. El volumen `task-data` mantiene SQLite entre reinicios y permite escribir como `appuser`. Este montaje evita ocultar el directorio de datos preparado en la imagen.

```sh
docker compose restart api
docker compose down
```

`docker compose down` conserva el volumen de datos.

## 7. Cargar diez tareas

En local, con el entorno activado:

```sh
python seed.py
python seed.py
python seed.py --force
```

La primera ejecución agrega diez tareas, cuatro completadas y seis pendientes. La segunda conserva los datos. `--force` reemplaza todas las tareas existentes dentro de una transacción.

Para cargar los datos en el contenedor:

```sh
docker compose exec -T api python -c 'import sys; exec(compile(sys.stdin.read(), "seed.py", "exec"))' < seed.py
```

Para reiniciar los datos del contenedor, agrega `--force` después del código de `python -c`.

El seed completa las cinco tareas y el comportamiento de reinicio que aparecen abreviados en la guía. La base local y la base de Docker son independientes.

## Verificación realizada

Las once pruebas pasaron. Se comprobaron la API local y en contenedor, Swagger, la identidad no privilegiada, la recarga al editar, la persistencia entre reinicios y las diez tareas iniciales. `evidencia.txt` en el ZIP conserva las salidas de la verificación.
