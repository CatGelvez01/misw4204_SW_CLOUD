# Arquitectura del Sistema - ANB Rising Stars Showcase

## Descripción General

ANB Rising Stars Showcase es una aplicación web escalable diseñada para gestionar la carga, procesamiento y votación de videos de baloncesto. La arquitectura sigue principios de escalabilidad, confiabilidad y separación de responsabilidades.

## Componentes Principales

### 1. API REST (FastAPI)
- **Responsabilidad**: Exponer endpoints para autenticación, gestión de videos y votación
- **Características**:
  - Autenticación basada en JWT
  - Validación de datos con Pydantic
  - Documentación automática con OpenAPI
  - Manejo de errores consistente

### 2. Base de Datos (PostgreSQL)
- **Responsabilidad**: Persistencia de datos
- **Tablas principales**:
  - `users`: Información de jugadores
  - `videos`: Metadatos de videos
  - `votes`: Registro de votos

### 3. Message Broker (Redis)
- **Responsabilidad**: Intermediario para tareas asíncronas
- **Funciones**:
  - Cola de tareas para Celery
  - Cache para rankings
  - Sesiones de usuario

### 4. Worker Asíncrono (Celery)
- **Responsabilidad**: Procesamiento de videos en segundo plano
- **Tareas**:
  - Recorte de duración
  - Ajuste de resolución
  - Adición de watermark
  - Eliminación de audio

### 5. Servidor Web (Nginx)
- **Responsabilidad**: Proxy inverso y balanceo de carga
- **Funciones**:
  - Enrutamiento de solicitudes
  - Compresión GZIP
  - Servicio de archivos estáticos
  - Límite de tamaño de cuerpo

## Flujo de Datos

### Registro de Usuario
```
Cliente → API (POST /api/auth/signup) → PostgreSQL
```

### Carga de Video
```
Cliente → API (POST /api/videos/upload) →
  ├─ Guardar archivo en disco
  ├─ Crear registro en BD
  └─ Encolar tarea en Redis
```

### Procesamiento de Video
```
Redis (Cola) → Celery Worker →
  ├─ Leer video original
  ├─ Procesar (trim, resolución, watermark, audio)
  ├─ Guardar video procesado
  └─ Actualizar estado en BD
```

### Votación
```
Cliente → API (POST /api/public/videos/{id}/vote) →
  ├─ Validar usuario y video
  ├─ Crear registro de voto en BD
  └─ Invalidar cache de ranking
```

### Ranking
```
Cliente → API (GET /api/public/rankings) →
  ├─ Verificar cache en Redis
  ├─ Si no existe: Calcular desde BD
  ├─ Guardar en cache (TTL: 5 min)
  └─ Retornar resultado
```

## Modelos de Datos

### User
```
- id (PK)
- first_name
- last_name
- email (UNIQUE)
- hashed_password
- city
- country
- created_at
- updated_at
```

### Video
```
- id (PK)
- owner_id (FK → User)
- title
- status (uploaded, processing, processed, failed)
- original_filename
- original_path
- processed_path
- task_id
- uploaded_at
- processed_at
- created_at
- updated_at
```

### Vote
```
- id (PK)
- voter_id (FK → User)
- video_id (FK → Video)
- created_at
- UNIQUE(voter_id, video_id)
```

## Seguridad

### Autenticación
- JWT con expiración configurable
- Contraseñas hasheadas con Argon2 (sin límite de bytes)
- Validación de email único

### Autorización
- Endpoints protegidos requieren token JWT válido
- Usuarios solo pueden acceder a sus propios videos
- Votación limitada a 1 voto por usuario por video

### Validación
- Validación de tipos con Pydantic
- Límite de tamaño de archivo (100MB)
- Validación de formato de video (MP4)

## Escalabilidad

### Horizontal
- Múltiples instancias de API detrás de Nginx
- Múltiples workers de Celery
- PostgreSQL con replicación (futuro)

### Vertical
- Configuración de recursos en Docker Compose
- Ajuste de concurrencia de workers
- Optimización de queries

### Caching
- Redis para rankings (TTL: 5 min)
- Posibilidad de agregar cache de videos procesados

## Despliegue

### Contenedorización
- Dockerfile con Python 3.11 slim
- Instalación de dependencias del sistema (ffmpeg, postgresql-client)
- Volúmenes para uploads y processed

### Orquestación
- Docker Compose con 5 servicios:
  1. PostgreSQL
  2. Redis
  3. FastAPI Backend
  4. Celery Worker
  5. Nginx

### Configuración
- Variables de entorno en `.env`
- Health checks para cada servicio
- Redes aisladas entre servicios

## Monitoreo y Logging

### Logs
- Nivel configurable (INFO, DEBUG, etc.)
- Acceso a logs de Nginx
- Logs de Celery para tareas

### Health Checks
- Endpoint `/health` para verificar estado
- Health checks en Docker Compose
- Verificación de conectividad a BD y Redis

## Próximos Pasos

1. Implementar procesamiento real de videos con moviepy
2. Agregar autenticación de dos factores
3. Implementar notificaciones en tiempo real
4. Agregar métricas y monitoreo con Prometheus
5. Configurar CI/CD con GitHub Actions
6. Agregar pruebas de carga
7. Implementar análisis de SonarQube
