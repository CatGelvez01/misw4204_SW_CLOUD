# Diagrama de Componentes - ANB Rising Stars Showcase

## Representación de Componentes

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                        ARQUITECTURA DE COMPONENTES                       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    CAPA DE PRESENTACIÓN                           │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │                    Nginx (Proxy Inverso)                │   │ │
│  │  │  - Balanceo de carga                                    │   │ │
│  │  │  - Compresión de respuestas                             │   │ │
│  │  │  - Caché de contenido estático                          │   │ │
│  │  │  - Rate limiting                                        │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    CAPA DE APLICACIÓN                             │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │                  FastAPI Backend                         │   │ │
│  │  │                                                          │   │ │
│  │  │  ┌────────────────┐  ┌────────────────┐               │   │ │
│  │  │  │  API Routes    │  │  Middlewares   │               │   │ │
│  │  │  │  - /auth       │  │  - CORS        │               │   │ │
│  │  │  │  - /videos     │  │  - Auth        │               │   │ │
│  │  │  │  - /public     │  │  - Logging     │               │   │ │
│  │  │  └────────────────┘  └────────────────┘               │   │ │
│  │  │                                                          │   │ │
│  │  │  ┌────────────────┐  ┌────────────────┐               │   │ │
│  │  │  │  Services      │  │  Schemas       │               │   │ │
│  │  │  │  - Auth        │  │  - Request     │               │   │ │
│  │  │  │  - Video       │  │  - Response    │               │   │ │
│  │  │  │  - Vote        │  │  - Error       │               │   │ │
│  │  │  └────────────────┘  └────────────────┘               │   │ │
│  │  │                                                          │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                    ┌────────────┼────────────┐                          │
│                    │            │            │                          │
│                    ▼            ▼            ▼                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    CAPA DE DATOS                                  │ │
│  │                                                                    │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │ │
│  │  │   PostgreSQL     │  │     Redis        │                     │ │
│  │  │   (Database)     │  │     (Cache)      │                     │ │
│  │  │                  │  │                  │                     │ │
│  │  │  - Users         │  │  - Sessions      │                     │ │
│  │  │  - Videos        │  │  - Task Queue    │                     │ │
│  │  │  - Votes         │  │  - Results       │                     │ │
│  │  │  - Índices       │  │  - Caché         │                     │ │
│  │  └──────────────────┘  └──────────────────┘                     │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    CAPA DE PROCESAMIENTO                          │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │              Celery Worker                              │   │ │
│  │  │                                                          │   │ │
│  │  │  ┌────────────────────────────────────────────────┐    │   │ │
│  │  │  │  Tareas Asíncronas                             │    │   │ │
│  │  │  │  - process_video_task                          │    │   │ │
│  │  │  │    * Validación de video                       │    │   │ │
│  │  │  │    * Recorte de duración (30s)                 │    │   │ │
│  │  │  │    * Ajuste de resolución (720p, 16:9)        │    │   │ │
│  │  │  │    * Agregar marca de agua (ANB)              │    │   │ │
│  │  │  │    * Eliminar audio                            │    │   │ │
│  │  │  │    * Actualizar estado en BD                   │    │   │ │
│  │  │  └────────────────────────────────────────────────┘    │   │ │
│  │  │                                                          │   │ │
│  │  │  Características:                                        │   │ │
│  │  │  - Reintentos automáticos                               │   │ │
│  │  │  - Manejo de errores                                    │   │ │
│  │  │  - Logging detallado                                    │   │ │
│  │  │  - Escalabilidad horizontal                             │   │ │
│  │  │                                                          │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │                    ALMACENAMIENTO DE ARCHIVOS                     │ │
│  │                                                                    │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │ │
│  │  │  /uploads        │  │  /processed      │                     │ │
│  │  │  (Videos orig.)  │  │  (Videos proc.)  │                     │ │
│  │  │                  │  │                  │                     │ │
│  │  │  - Validación    │  │  - Transformados │                     │ │
│  │  │  - Almacenaje    │  │  - Listos para   │                     │ │
│  │  │  - Temporal      │  │    descargar     │                     │ │
│  │  └──────────────────┘  └──────────────────┘                     │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Descripción de Componentes

### Backend (FastAPI)

**Responsabilidades**:
- Gestión de autenticación y autorización
- Validación de solicitudes
- Orquestación de tareas asíncronas
- Respuestas HTTP estructuradas
- Documentación automática (Swagger)

**Módulos**:
- `app/api/`: Endpoints y rutas
- `app/models/`: Modelos de datos
- `app/schemas/`: Esquemas de validación
- `app/services/`: Lógica de negocio
- `app/core/`: Configuración y utilidades

---

### Worker (Celery)

**Responsabilidades**:
- Procesamiento asíncrono de videos
- Transformación de archivos
- Actualización de estado en BD
- Manejo de errores y reintentos
- Logging de operaciones

**Tareas**:
- `process_video_task`: Procesamiento completo de video

---

### Message Broker (Redis)

**Responsabilidades**:
- Cola de tareas (Celery)
- Almacenamiento de resultados
- Caché de sesiones
- Almacenamiento temporal de datos

**Configuración**:
- Base 0: Caché general
- Base 1: Cola de Celery
- Base 2: Resultados de Celery

---

### Base de Datos (PostgreSQL)

**Responsabilidades**:
- Almacenamiento persistente
- Integridad referencial
- Índices para optimización
- Auditoría con timestamps

**Tablas**:
- `users`: Información de jugadores
- `videos`: Metadatos de videos
- `votes`: Registro de votaciones

---

### Proxy Inverso (Nginx)

**Responsabilidades**:
- Enrutamiento de solicitudes
- Balanceo de carga
- Compresión de respuestas
- Caché de contenido estático
- Protección contra ataques

---

## Interacciones entre Componentes

```
Cliente HTTP
    │
    ▼
Nginx (Proxy)
    │
    ▼
FastAPI Backend
    │
    ├─► PostgreSQL (lectura/escritura)
    │
    ├─► Redis (caché)
    │
    └─► Celery (encolamiento de tareas)
            │
            ▼
        Celery Worker
            │
            ├─► PostgreSQL (actualización de estado)
            │
            ├─► Redis (almacenamiento de resultados)
            │
            └─► Almacenamiento de archivos
```
