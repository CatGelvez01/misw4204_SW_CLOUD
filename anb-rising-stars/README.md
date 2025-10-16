# ANB Rising Stars Showcase

Plataforma web para descubrir talentos emergentes de baloncesto a través de videos y votación comunitaria.

## 📋 Descripción

**ANB Rising Stars Showcase** es una plataforma que permite a jugadores aficionados de baloncesto subir videos demostrando sus habilidades (20-60 segundos, 1080p+). Los videos se procesan automáticamente (recortados a 30s, ajustados a 720p 16:9, con watermark de ANB, sin audio) y se ponen disponibles para votación pública, generando un ranking dinámico de los mejores talentos.

## ✨ Características

- 🔐 Autenticación JWT segura
- 📹 Carga y validación de videos
- ⚙️ Procesamiento asíncrono de videos (Celery + Redis)
- 🗳️ Sistema de votación pública
- 📊 Ranking dinámico con caching
- 📚 API REST documentada (OpenAPI/Swagger)
- 🐳 Despliegue con Docker Compose
- ✅ Tests unitarios

## 🛠️ Stack Técnico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python 3.11 + FastAPI |
| Base de datos | PostgreSQL |
| Cache/Message Broker | Redis |
| Procesamiento asíncrono | Celery |
| Servidor web | Nginx |
| Contenedorización | Docker + Docker Compose |
| Autenticación | JWT (python-jose) |
| Validación | Pydantic |
| Hashing de contraseñas | Argon2 |
| Linting/Formatting | Ruff |

## 📦 Requisitos Previos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Git

## 🚀 Inicio Rápido

Para empezar en 5 minutos, consulta [QUICKSTART.md](./QUICKSTART.md).

## 📖 Instalación Completa

### Con Docker Compose (Recomendado)

```bash
# Clonar repositorio
git clone <repository-url>
cd anb-rising-stars

# Copiar archivo de configuración
cp .env.example .env

# Iniciar servicios
docker compose up -d

# Verificar estado
docker compose ps
```

**Acceso:**
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar BD y cache
docker compose up -d postgres redis

# Terminal 1: Backend
python run.py

# Terminal 2: Worker Celery
celery -A app.tasks.celery_app worker --loglevel=info
```

## 🔌 Endpoints Principales

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Registrar usuario | ❌ |
| POST | `/api/auth/login` | Iniciar sesión | ❌ |
| POST | `/api/videos/upload` | Subir video | ✅ |
| GET | `/api/videos` | Mis videos | ✅ |
| GET | `/api/videos/{id}` | Detalle de video | ✅ |
| DELETE | `/api/videos/{id}` | Eliminar video | ✅ |
| GET | `/api/public/videos` | Videos para votar | ❌ |
| POST | `/api/public/videos/{id}/vote` | Votar | ✅ |
| GET | `/api/public/rankings` | Ranking | ❌ |

**Documentación interactiva:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ✅ Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/
```

## 📁 Estructura del Proyecto

```
anb-rising-stars/
├── app/
│   ├── api/              # Endpoints (auth, videos, votes)
│   ├── core/             # Config, BD, seguridad
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Esquemas Pydantic
│   ├── services/         # Lógica de negocio
│   ├── tasks/            # Tareas Celery
│   └── main.py           # App FastAPI
├── nginx/                # Configuración Nginx
├── tests/                # Tests unitarios
├── docs/                 # Documentación
├── docker-compose.yml    # Orquestación
├── requirements.txt      # Dependencias
└── QUICKSTART.md         # Guía rápida
```

## 📚 Documentación

- **[QUICKSTART.md](./QUICKSTART.md)** - Inicio rápido (5 minutos)
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Arquitectura del sistema
- **[docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)** - Guía de desarrollo
- **[docs/API_ENDPOINTS.md](./docs/API_ENDPOINTS.md)** - Especificación de endpoints

## 🔧 Herramientas de Desarrollo

- **Ruff** - Linting y formatting (reemplaza black, flake8, isort) - Se ejecuta automáticamente con pre-commit
- **Pre-commit** - Hooks automáticos antes de commits
- **Pytest** - Framework de testing
- **Docker** - Contenedorización

## 📝 Estándar de Commits

Usamos [Gitmoji](https://gitmoji.dev) para commits semánticos:

```bash
# Instalar pre-commit (incluye Ruff)
pip install pre-commit
pre-commit install

# Hacer commit con gitmoji + mensaje en inglés (minúsculas)
git commit -m "✨ introduce new features"
git commit -m "🐛 fix a bug"
git commit -m "📝 add or update documentation"
git commit -m "♻️ refactor code"
git commit -m "✅ add or update tests"
git commit -m "🚀 deploy stuff"
git commit -m "🔧 add or update configuration files"
```

**Gitmojis comunes:**
- ✨ `:sparkles:` Introduce new features
- 🐛 `:bug:` Fix a bug
- 📝 `:memo:` Add or update documentation
- ♻️ `:recycle:` Refactor code
- ✅ `:white_check_mark:` Add or update tests
- 🚀 `:rocket:` Deploy stuff
- 🔧 `:wrench:` Add or update configuration files
- 🎨 `:art:` Improve structure/format of code
- 🔥 `:fire:` Remove code or files

## 📄 Licencia

Proyecto académico - MISW4204: Software en la Nube
