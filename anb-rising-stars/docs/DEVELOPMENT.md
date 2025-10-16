# Guía de Desarrollo - ANB Rising Stars Showcase

## Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.11+
- PostgreSQL
- Redis
- Docker y Docker Compose (opcional)

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd anb-rising-stars
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
pip install pre-commit
```

4. **Configurar pre-commit hooks**
```bash
pre-commit install
```

5. **Crear archivo .env**
```bash
cp .env.example .env
```

6. **Iniciar servicios con Docker**
```bash
docker compose up -d postgres redis
```

7. **Ejecutar la aplicación**
```bash
# Terminal 1: API
python run.py

# Terminal 2: Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info
```

## Estructura de Código

### Convenciones de Nombres
- **Módulos**: snake_case (ej: `video_processor.py`)
- **Clases**: PascalCase (ej: `VideoProcessor`)
- **Funciones**: snake_case (ej: `process_video()`)
- **Constantes**: UPPER_SNAKE_CASE (ej: `MAX_FILE_SIZE`)

### Organización de Archivos
```
app/
├── api/          # Routers y endpoints
├── core/         # Configuración central
├── models/       # Modelos SQLAlchemy
├── schemas/      # Esquemas Pydantic
├── services/     # Lógica de negocio
├── tasks/        # Tareas Celery
├── utils/        # Funciones auxiliares
└── middleware/   # Middleware personalizado
```

## Desarrollo de Nuevos Endpoints

### Paso 1: Crear el Schema (Pydantic)
```python
# app/schemas/example.py
from pydantic import BaseModel, Field

class ExampleRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class ExampleResponse(BaseModel):
    id: int
    name: str
```

### Paso 2: Crear el Modelo (SQLAlchemy)
```python
# app/models/example.py
from sqlalchemy import Column, String, Integer
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
```

### Paso 3: Crear el Endpoint
```python
# app/api/example.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Example
from app.schemas import ExampleRequest, ExampleResponse

router = APIRouter()

@router.post("/examples", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleRequest,
    db: Session = Depends(get_db),
):
    """Create a new example."""
    example = Example(name=data.name)
    db.add(example)
    db.commit()
    db.refresh(example)
    return example
```

### Paso 4: Incluir el Router
```python
# app/main.py
from app.api import example
app.include_router(example.router, prefix="/api/examples", tags=["Examples"])
```

## Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py

# Con cobertura
pytest --cov=app tests/

# Con output detallado
pytest -v
```

### Escribir Tests
```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_example():
    response = client.post("/api/examples", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

## Calidad de Código

### Ruff (Linting y Formatting)

Ruff reemplaza black, flake8 e isort. Se ejecuta automáticamente con pre-commit.

```bash
# Ejecutar manualmente
ruff check --fix app/
ruff format app/

# Ver problemas sin arreglar
ruff check app/
```

### Pre-commit Hooks

Los hooks se ejecutan automáticamente antes de cada commit:

```bash
# Ejecutar manualmente todos los hooks
pre-commit run --all-files

# Hacer commit (los hooks se ejecutan automáticamente)
git commit -m "✨ add new feature"
```

**Nota:** Si pre-commit falla, arregla los problemas y vuelve a intentar el commit.

## Estándar de Commits

Usamos [Gitmoji](https://gitmoji.dev) para commits semánticos. El formato es:

```
<gitmoji> <mensaje en inglés minúsculas>
```

### Ejemplos

```bash
# Nueva funcionalidad
git commit -m "✨ introduce user authentication with jwt"

# Corrección de bug
git commit -m "🐛 fix video upload validation"

# Documentación
git commit -m "📝 add or update api endpoints documentation"

# Refactorización
git commit -m "♻️ refactor video processor service"

# Tests
git commit -m "✅ add tests for auth endpoints"

# Configuración
git commit -m "🔧 add or update docker compose configuration"

# Despliegue
git commit -m "🚀 deploy to production"

# Mejorar estructura
git commit -m "🎨 improve code structure and format"

# Eliminar código
git commit -m "🔥 remove unused video processing code"
```

### Gitmojis Comunes

| Emoji | Código | Descripción |
|-------|--------|-------------|
| ✨ | `:sparkles:` | Introduce new features |
| 🐛 | `:bug:` | Fix a bug |
| 📝 | `:memo:` | Add or update documentation |
| ♻️ | `:recycle:` | Refactor code |
| ✅ | `:white_check_mark:` | Add or update tests |
| 🚀 | `:rocket:` | Deploy stuff |
| 🔧 | `:wrench:` | Add or update configuration files |
| 🎨 | `:art:` | Improve structure/format of code |
| 🔥 | `:fire:` | Remove code or files |
| ⬆️ | `:arrow_up:` | Upgrade dependencies |
| ⬇️ | `:arrow_down:` | Downgrade dependencies |

**Ver más en:** https://gitmoji.dev

## Tareas Asíncronas

### Crear una Nueva Tarea
```python
# app/tasks/example_tasks.py
from celery import shared_task
from app.core.database import SessionLocal

@shared_task(bind=True, max_retries=3)
def example_task(self, param: str):
    db = SessionLocal()
    try:
        # Lógica de la tarea
        return {"status": "success"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
```

### Encolar una Tarea
```python
from app.tasks.example_tasks import example_task

# Encolar inmediatamente
example_task.delay("param_value")

# Encolar con retraso
example_task.apply_async(args=["param_value"], countdown=60)
```

## Migraciones de Base de Datos

### Crear una Migración
```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar Migraciones
```bash
alembic upgrade head
```

### Revertir Migraciones
```bash
alembic downgrade -1
```

## Variables de Entorno

### Desarrollo
```
DEBUG=True
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/anb_rising_stars
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
```

### Producción
```
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@prod-db:5432/anb_rising_stars
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=<strong-random-key>
```

## Debugging

### Logs
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.error("Mensaje de error")
```

### Breakpoints
```python
import pdb; pdb.set_trace()
```

### FastAPI Debug
```python
# En main.py
app = FastAPI(debug=True)
```

## Recursos Útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
