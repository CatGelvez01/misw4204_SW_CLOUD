# Arquitectura del Sistema - ANB Rising Stars Showcase

## Diagramas C4

### Nivel 1: Contexto del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    ANB Rising Stars Showcase                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  Plataforma web para carga, almacenamiento y votación   │  │
│  │  de videos de jugadores de baloncesto                   │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────────┐   │
│  │   Jugadores      │              │   Público General    │   │
│  │   (Usuarios)     │◄────────────►│   (Votantes)         │   │
│  └──────────────────┘              └──────────────────────┘   │
│           │                                 │                  │
│           └─────────────┬───────────────────┘                  │
│                         │                                      │
│                         ▼                                      │
│           ┌─────────────────────────────┐                     │
│           │  ANB Rising Stars API REST  │                     │
│           │  (FastAPI + PostgreSQL)     │                     │
│           └─────────────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Nivel 2: Contenedores

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                    ANB Rising Stars Showcase                         │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Docker Network                            │ │
│  │                                                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │ │
│  │  │   Nginx      │  │   FastAPI    │  │   PostgreSQL     │   │ │
│  │  │   (Proxy)    │─►│   (Backend)  │─►│   (Database)     │   │ │
│  │  │              │  │              │  │                  │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │ │
│  │         ▲                  │                                  │ │
│  │         │                  │                                  │ │
│  │         │          ┌───────┴────────┐                        │ │
│  │         │          │                │                        │ │
│  │         │          ▼                ▼                        │ │
│  │         │      ┌──────────┐    ┌──────────────┐             │ │
│  │         │      │  Redis   │    │   Celery     │             │ │
│  │         │      │  (Cache) │    │   (Worker)   │             │ │
│  │         │      └──────────┘    └──────────────┘             │ │
│  │         │                                                    │ │
│  │  ┌──────┴────────────────────────────────────────────────┐  │ │
│  │  │              Almacenamiento de Archivos              │  │ │
│  │  │  - /uploads (videos originales)                      │  │ │
│  │  │  - /processed (videos procesados)                    │  │ │
│  │  │  - /assets (recursos de la aplicación)              │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Decisiones de Diseño

### 1. Framework: FastAPI

**Justificación**:
- Alto rendimiento y bajo overhead
- Validación automática de datos con Pydantic
- Documentación automática con Swagger/OpenAPI
- Soporte nativo para async/await
- Ideal para APIs REST escalables

### 2. Base de Datos: PostgreSQL

**Justificación**:
- ACID compliance para integridad de datos
- Soporte para relaciones complejas
- Índices eficientes para consultas frecuentes
- Escalabilidad horizontal con replicación
- Mejor que SQLite para producción

### 3. Message Broker: Redis

**Justificación**:
- Bajo latency para colas de tareas
- Soporte para Celery (task queue)
- Almacenamiento en memoria para caché
- Persistencia opcional
- Fácil de desplegar en contenedores

### 4. Task Queue: Celery

**Justificación**:
- Procesamiento asíncrono de videos
- Reintentos automáticos con backoff
- Monitoreo de tareas
- Escalabilidad horizontal con múltiples workers
- Integración nativa con FastAPI

### 5. Proxy Inverso: Nginx

**Justificación**:
- Balanceo de carga
- Compresión de respuestas
- Caché de contenido estático
- Seguridad y protección contra ataques
- Mejor rendimiento que exponer FastAPI directamente

### 6. Contenedorización: Docker

**Justificación**:
- Portabilidad entre entornos
- Reproducibilidad de despliegues
- Aislamiento de servicios
- Facilita escalabilidad horizontal
- Estándar de la industria

---

## Patrones Arquitectónicos

### 1. Patrón MVC (Model-View-Controller)

- **Models**: Definición de entidades en `app/models/`
- **Views**: Schemas de respuesta en `app/schemas/`
- **Controllers**: Endpoints en `app/api/`

### 2. Patrón Repository

- Abstracción de acceso a datos
- Facilita testing y cambios de BD

### 3. Patrón Dependency Injection

- FastAPI Depends para inyección de dependencias
- Facilita testing y reutilización de código

### 4. Patrón Async/Await

- Operaciones no bloqueantes
- Mayor concurrencia con menos recursos

### 5. Patrón Task Queue

- Procesamiento asíncrono de videos
- Desacoplamiento entre API y procesamiento

---

## Flujo de Datos

```
1. Usuario sube video
   ↓
2. API valida y almacena en /uploads
   ↓
3. API crea tarea Celery
   ↓
4. Worker Celery procesa video
   ↓
5. Video procesado se almacena en /processed
   ↓
6. Estado en BD se actualiza a "processed"
   ↓
7. Usuario puede descargar video procesado
```

---

## Seguridad

- **Autenticación**: JWT tokens
- **Autorización**: Validación de permisos por endpoint
- **Validación**: Pydantic schemas
- **Hashing**: bcrypt para contraseñas
- **CORS**: Configurado para orígenes permitidos
- **Rate Limiting**: Implementado en Nginx
