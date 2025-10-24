# Documentación de Despliegue - ANB Rising Stars Showcase

## Infraestructura

### Arquitectura de Contenedores

La aplicación está completamente containerizada usando Docker y Docker Compose. La infraestructura consta de 5 servicios principales:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    INFRAESTRUCTURA DOCKER                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Nginx (Proxy Inverso)                                   │  │
│  │  - Puerto: 8080                                          │  │
│  │  - Balanceo de carga                                     │  │
│  │  - Compresión de respuestas                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend                                         │  │
│  │  - Puerto: 8000 (interno)                                │  │
│  │  - Uvicorn ASGI server                                   │  │
│  │  - Volumen: /app/uploads, /app/processed                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│          ┌───────────────┼───────────────┐                     │
│          │               │               │                     │
│          ▼               ▼               ▼                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ PostgreSQL   │ │ Redis        │ │ Celery       │           │
│  │ - Puerto:    │ │ - Puerto:    │ │ Worker       │           │
│  │   5432       │ │   6379       │ │ - Procesa    │           │
│  │ - Volumen:   │ │ - Volumen:   │ │   videos     │           │
│  │   postgres   │ │   redis_data │ │ - Escalable  │           │
│  │   _data      │ │              │ │   horizontal │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Servicios

### 1. PostgreSQL 16

**Propósito**: Base de datos relacional persistente

**Configuración**:
- **Imagen**: `postgres:16`
- **Puerto**: 5432 (interno)
- **Volumen**: `postgres_data` (/var/lib/postgresql/data)
- **Variables de Entorno**:
  - `POSTGRES_USER`: postgres
  - `POSTGRES_PASSWORD`: postgres
  - `POSTGRES_DB`: anb_db

**Tablas**:
- `users`: Información de jugadores
- `videos`: Metadatos de videos
- `votes`: Registro de votaciones

**Inicialización**: Automática con SQLAlchemy ORM

---

### 2. Redis 7

**Propósito**: Message broker y caché

**Configuración**:
- **Imagen**: `redis:7`
- **Puerto**: 6379 (interno)
- **Volumen**: `redis_data` (/data)
- **Comando**: `redis-server --appendonly yes`

**Uso**:
- Base 0: Caché general
- Base 1: Cola de tareas Celery
- Base 2: Resultados de Celery

---

### 3. FastAPI Backend

**Propósito**: API REST principal

**Configuración**:
- **Imagen**: Construida desde `Dockerfile`
- **Puerto**: 8000 (interno), 8080 (externo vía Nginx)
- **Volúmenes**:
  - `/app/uploads`: Videos originales cargados
  - `/app/processed`: Videos procesados
- **Comando**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Dependencias**: PostgreSQL, Redis

**Variables de Entorno**:
```
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/anb_db
REDIS_URL=redis://redis:6379
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
SECRET_KEY=<clave-secreta>
ACCESS_TOKEN_EXPIRE_MINUTES=60
MAX_FILE_SIZE=104857600
UPLOAD_DIR=/app/uploads
PROCESSED_DIR=/app/processed
```

---

### 4. Celery Worker

**Propósito**: Procesamiento asíncrono de videos

**Configuración**:
- **Imagen**: Construida desde `Dockerfile`
- **Comando**: `celery -A app.tasks.celery_app worker --loglevel=info`
- **Volúmenes**:
  - `/app/uploads`: Lectura de videos originales
  - `/app/processed`: Escritura de videos procesados
- **Dependencias**: PostgreSQL, Redis

**Tareas**:
- `process_video_task`: Procesamiento completo de video

**Características**:
- Reintentos automáticos (hasta 3 intentos)
- Timeout: 3600 segundos (1 hora)
- Logging detallado

---

### 5. Nginx

**Propósito**: Proxy inverso y balanceo de carga

**Configuración**:
- **Imagen**: `nginx:latest`
- **Puerto**: 8080 (externo)
- **Volumen**: Configuración personalizada

**Funcionalidades**:
- Enrutamiento de solicitudes al backend
- Compresión gzip de respuestas
- Caché de contenido estático
- Rate limiting
- Servir archivos estáticos (uploads, processed)

**Rutas**:
- `/api/*` → Backend FastAPI
- `/uploads/*` → Archivos originales
- `/processed/*` → Archivos procesados
- `/docs` → Swagger UI
- `/redoc` → ReDoc

---

## Red Docker

**Nombre**: `anb_network`

**Tipo**: Bridge

**Servicios conectados**:
- postgres
- redis
- backend
- celery_worker
- nginx

**Comunicación interna**: Los servicios se comunican por nombre de servicio (ej: `postgres:5432`)

---

## Volúmenes

| Nombre | Punto de Montaje | Propósito |
|--------|------------------|-----------|
| `postgres_data` | `/var/lib/postgresql/data` | Persistencia de BD |
| `redis_data` | `/data` | Persistencia de Redis |
| `uploads` | `/app/uploads` | Videos originales |
| `processed` | `/app/processed` | Videos procesados |

---

## Requisitos Previos

### Sistema Operativo
- Linux, macOS o Windows (con WSL2)
- Mínimo 4GB RAM
- Mínimo 10GB espacio en disco

### Software Requerido
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Verificar Instalación
```bash
docker --version
docker-compose --version
```

---

## Guía de Despliegue

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/anb-rising-stars.git
cd anb-rising-stars
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Base de Datos
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/anb_db

# Redis
REDIS_URL=redis://redis:6379

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura-aqui

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Archivos
MAX_FILE_SIZE=104857600
UPLOAD_DIR=/app/uploads
PROCESSED_DIR=/app/processed
```

### 3. Construir Imágenes

```bash
docker-compose build
```

### 4. Iniciar Servicios

```bash
docker-compose up -d
```

**Verificar estado**:
```bash
docker-compose ps
```

**Esperado**:
```
NAME                COMMAND                  SERVICE             STATUS
anb-postgres        "docker-entrypoint.s…"   postgres            Up 2 minutes
anb-redis           "redis-server --appe…"   redis               Up 2 minutes
anb-backend         "uvicorn app.main:ap…"   backend             Up 2 minutes
anb-celery-worker   "celery -A app.tasks…"   celery_worker       Up 2 minutes
anb-nginx           "nginx -g daemon off…"   nginx               Up 2 minutes
```

### 5. Verificar Conectividad

```bash
# Verificar API
curl http://localhost:8080/docs

# Verificar BD
docker-compose exec postgres psql -U postgres -d anb_db -c "SELECT version();"

# Verificar Redis
docker-compose exec redis redis-cli ping
```

---

## Operaciones Comunes

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Ejecutar Comandos en Contenedores

```bash
# Acceder a la BD
docker-compose exec postgres psql -U postgres -d anb_db

# Ejecutar comando en backend
docker-compose exec backend python -c "from app.models import User; print('OK')"

# Verificar cola de Celery
docker-compose exec redis redis-cli -n 1 LLEN celery
```

### Detener Servicios

```bash
# Detener sin eliminar
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos)
docker-compose down -v
```

### Reiniciar Servicios

```bash
# Reiniciar todos
docker-compose restart

# Reiniciar servicio específico
docker-compose restart backend
```

---

## Troubleshooting

### Puerto 8080 en uso

```bash
# Encontrar proceso usando puerto 8080
lsof -i :8080

# Cambiar puerto en docker-compose.yml
# Cambiar: "8080:8080" por "8081:8080"
```

### Base de datos no inicializa

```bash
# Eliminar volumen y reiniciar
docker-compose down -v
docker-compose up -d
```

### Celery no procesa tareas

```bash
# Verificar logs del worker
docker-compose logs celery_worker

# Verificar cola en Redis
docker-compose exec redis redis-cli -n 1 LLEN celery

# Reiniciar worker
docker-compose restart celery_worker
```

### Archivos no se guardan

```bash
# Verificar permisos de volúmenes
docker-compose exec backend ls -la /app/uploads
docker-compose exec backend ls -la /app/processed

# Crear directorios si no existen
docker-compose exec backend mkdir -p /app/uploads /app/processed
```

---

## Monitoreo

### Métricas de Contenedores

```bash
# Ver uso de recursos
docker stats

# Ver detalles de contenedor
docker inspect anb-backend
```

### Logs de Aplicación

```bash
# Seguir logs en tiempo real
docker-compose logs -f backend

# Buscar errores
docker-compose logs backend | grep ERROR
```

### Verificar Salud de Servicios

```bash
# Verificar API
curl -s http://localhost:8080/docs | head -20

# Verificar BD
docker-compose exec postgres pg_isready

# Verificar Redis
docker-compose exec redis redis-cli ping
```

---

## Escalabilidad

### Escalar Celery Workers

```bash
# Aumentar a 3 workers
docker-compose up -d --scale celery_worker=3

# Verificar
docker-compose ps
```

### Optimizaciones

1. **Aumentar memoria**: Modificar `docker-compose.yml`
2. **Aumentar workers**: Escalar servicio Celery
3. **Caché**: Configurar Redis para caché de consultas
4. **Índices BD**: Agregar índices en tablas frecuentes

---

## Seguridad en Producción

### Cambios Recomendados

1. **Cambiar contraseñas**:
   - PostgreSQL: `POSTGRES_PASSWORD`
   - Redis: Agregar autenticación

2. **Usar variables de entorno seguras**:
   - No commitear `.env`
   - Usar secrets manager

3. **Configurar HTTPS**:
   - Agregar certificados SSL
   - Redirigir HTTP a HTTPS

4. **Limitar acceso**:
   - Firewall
   - VPN
   - IP whitelist

5. **Backups**:
   - Automatizar backups de BD
   - Almacenar en ubicación segura

---

## Backup y Recuperación

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec postgres pg_dump -U postgres anb_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres anb_db < backup.sql
```

### Backup de Volúmenes

```bash
# Backup de uploads
docker run --rm -v anb-rising-stars_uploads:/data -v $(pwd):/backup \
  alpine tar czf /backup/uploads.tar.gz -C /data .

# Restaurar uploads
docker run --rm -v anb-rising-stars_uploads:/data -v $(pwd):/backup \
  alpine tar xzf /backup/uploads.tar.gz -C /data
```
