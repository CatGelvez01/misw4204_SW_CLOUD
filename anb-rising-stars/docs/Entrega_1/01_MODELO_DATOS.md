# Modelo de Datos - ANB Rising Stars Showcase

## Diagrama Entidad-Relación (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          MODELO DE DATOS                                   │
│                                                                             │
│  ┌──────────────────────┐         ┌──────────────────────┐                 │
│  │      USERS           │         │      VIDEOS          │                 │
│  ├──────────────────────┤         ├──────────────────────┤                 │
│  │ id (PK)              │◄────────│ id (PK, UUID)        │                 │
│  │ first_name           │    1:N  │ owner_id (FK)        │                 │
│  │ last_name            │         │ title                │                 │
│  │ email (UNIQUE)       │         │ status               │                 │
│  │ hashed_password      │         │ original_filename    │                 │
│  │ city                 │         │ original_path        │                 │
│  │ country              │         │ processed_path       │                 │
│  │ created_at           │         │ task_id              │                 │
│  │ updated_at           │         │ uploaded_at          │                 │
│  └──────────────────────┘         │ processed_at         │                 │
│           ▲                        │ created_at           │                 │
│           │                        │ updated_at           │                 │
│           │ 1:N                    └──────────────────────┘                 │
│           │                                 ▲                               │
│           │                                 │ 1:N                           │
│           │                                 │                               │
│           │                        ┌────────┴──────────┐                   │
│           │                        │      VOTES        │                   │
│           │                        ├───────────────────┤                   │
│           │                        │ id (PK)           │                   │
│           └────────────────────────│ voter_id (FK)     │                   │
│                                    │ video_id (FK)     │                   │
│                                    │ created_at        │                   │
│                                    │ UQ(voter_id,      │                   │
│                                    │    video_id)      │                   │
│                                    └───────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Especificación de Entidades

### 1. Entidad: USERS

**Descripción**: Almacena la información de los jugadores registrados en la plataforma.

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| id | Integer | PK, Auto-increment | Identificador único del usuario |
| first_name | String(100) | NOT NULL | Nombre del jugador |
| last_name | String(100) | NOT NULL | Apellido del jugador |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Correo electrónico único |
| hashed_password | String(255) | NOT NULL | Contraseña hasheada (bcrypt) |
| city | String(100) | NOT NULL | Ciudad del jugador |
| country | String(100) | NOT NULL | País del jugador |
| created_at | DateTime | NOT NULL, DEFAULT | Fecha de creación |
| updated_at | DateTime | NOT NULL, DEFAULT | Fecha de última actualización |

**Relaciones**:
- 1:N con VIDEOS (un usuario puede tener múltiples videos)
- 1:N con VOTES (un usuario puede votar múltiples videos)

---

### 2. Entidad: VIDEOS

**Descripción**: Almacena la información de los videos subidos por los jugadores.

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| id | UUID | PK | Identificador único del video |
| owner_id | Integer | FK(users.id), NOT NULL, INDEX | Usuario propietario del video |
| title | String(255) | NOT NULL | Título del video |
| status | Enum | NOT NULL, DEFAULT='uploaded' | Estado del video (uploaded, processing, processed, failed) |
| original_filename | String(255) | NOT NULL | Nombre original del archivo |
| original_path | String(500) | NOT NULL | Ruta del archivo original |
| processed_path | String(500) | NULLABLE | Ruta del archivo procesado |
| task_id | String(255) | NULLABLE, INDEX | ID de la tarea Celery |
| uploaded_at | DateTime | NOT NULL, DEFAULT | Fecha de carga |
| processed_at | DateTime | NULLABLE | Fecha de procesamiento completado |
| created_at | DateTime | NOT NULL, DEFAULT | Fecha de creación |
| updated_at | DateTime | NOT NULL, DEFAULT | Fecha de última actualización |

**Relaciones**:
- N:1 con USERS (muchos videos pertenecen a un usuario)
- 1:N con VOTES (un video puede recibir múltiples votos)

**Estados del Video**:
- `uploaded`: Video cargado, pendiente de procesamiento
- `processing`: Video en proceso de transformación
- `processed`: Video procesado exitosamente
- `failed`: Error durante el procesamiento

---

### 3. Entidad: VOTES

**Descripción**: Almacena los votos de los usuarios por los videos.

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| id | Integer | PK, Auto-increment | Identificador único del voto |
| voter_id | Integer | FK(users.id), NOT NULL, INDEX | Usuario que vota |
| video_id | UUID | FK(videos.id), NOT NULL, INDEX | Video votado |
| created_at | DateTime | NOT NULL, DEFAULT | Fecha del voto |
| UQ(voter_id, video_id) | Constraint | UNIQUE | Garantiza un voto por usuario por video |

**Relaciones**:
- N:1 con USERS (muchos votos de un usuario)
- N:1 con VIDEOS (muchos votos para un video)

**Restricciones de Negocio**:
- Un usuario solo puede votar una vez por video
- La restricción UNIQUE en (voter_id, video_id) previene votos duplicados

---

## Relaciones y Cardinalidades

| Relación | Cardinalidad | Descripción |
|----------|--------------|-------------|
| USERS → VIDEOS | 1:N | Un usuario puede subir múltiples videos |
| USERS → VOTES | 1:N | Un usuario puede emitir múltiples votos |
| VIDEOS → VOTES | 1:N | Un video puede recibir múltiples votos |

---

## Consideraciones de Diseño

1. **UUID para Videos**: Se utiliza UUID en lugar de Integer para mayor seguridad y evitar enumeración de IDs.

2. **Cascada de Eliminación**: Al eliminar un usuario, se eliminan automáticamente sus videos y votos asociados.

3. **Índices**: Se han creado índices en campos frecuentemente consultados (email, owner_id, task_id, voter_id, video_id).

4. **Timestamps**: Todas las entidades incluyen created_at y updated_at para auditoría.

5. **Restricción de Votos Únicos**: La restricción UNIQUE en (voter_id, video_id) previene fraude de votación.
