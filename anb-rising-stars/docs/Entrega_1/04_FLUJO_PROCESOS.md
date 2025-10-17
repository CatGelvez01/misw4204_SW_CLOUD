# Diagrama de Flujo de Procesos - ANB Rising Stars Showcase

## Flujo General del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    FLUJO GENERAL DE PROCESOS                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  1. REGISTRO DE USUARIO                                         │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Usuario                    API                    Base de Datos │  │
│  │     │                        │                          │       │  │
│  │     │─ POST /auth/signup ───►│                          │       │  │
│  │     │                        │─ Validar datos ────────►│       │  │
│  │     │                        │                          │       │  │
│  │     │                        │◄─ Usuario creado ───────│       │  │
│  │     │                        │                          │       │  │
│  │     │◄─ 201 Created ────────│                          │       │  │
│  │     │                        │                          │       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  2. AUTENTICACIÓN (LOGIN)                                       │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Usuario                    API                    Base de Datos │  │
│  │     │                        │                          │       │  │
│  │     │─ POST /auth/login ────►│                          │       │  │
│  │     │                        │─ Buscar usuario ───────►│       │  │
│  │     │                        │                          │       │  │
│  │     │                        │◄─ Usuario encontrado ───│       │  │
│  │     │                        │                          │       │  │
│  │     │                        │─ Verificar contraseña   │       │  │
│  │     │                        │─ Generar JWT token      │       │  │
│  │     │                        │                          │       │  │
│  │     │◄─ 200 OK + Token ─────│                          │       │  │
│  │     │                        │                          │       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Carga de Video

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    FLUJO DE CARGA DE VIDEO                              │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  3. CARGA DE VIDEO                                              │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Usuario                API              BD          Almacenaje │  │
│  │     │                    │               │              │       │  │
│  │     │─ POST /videos/upload (multipart)  │              │       │  │
│  │     │  + JWT token                       │              │       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Validar JWT │              │       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Validar archivo           │       │  │
│  │     │                    │  (formato, tamaño)         │       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Generar UUID │              │       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Guardar archivo ─────────►│       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Crear registro en BD ────►│       │  │
│  │     │                    │  (status: uploaded)        │       │  │
│  │     │                    │               │              │       │  │
│  │     │                    │─ Encolar tarea Celery      │       │  │
│  │     │                    │  (process_video_task)      │       │  │
│  │     │                    │               │              │       │  │
│  │     │◄─ 201 Created ────│               │              │       │  │
│  │     │  + video_id        │               │              │       │  │
│  │     │  + status          │               │              │       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Procesamiento Asíncrono

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                FLUJO DE PROCESAMIENTO ASÍNCRONO (Celery)                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  4. PROCESAMIENTO DE VIDEO                                      │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Redis Queue      Celery Worker        BD          Almacenaje  │  │
│  │     │                  │               │              │        │  │
│  │     │◄─ Tarea encolada │               │              │        │  │
│  │     │                  │               │              │        │  │
│  │     │─ Tarea disponible►│               │              │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Actualizar estado ────────►│        │  │
│  │     │                  │  (status: processing)       │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Leer video original ──────────────►│        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Validar duración           │        │  │
│  │     │                  │  (20-60 segundos)           │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Recortar a 30 segundos     │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Ajustar resolución         │        │  │
│  │     │                  │  (720p, 16:9)               │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Agregar marca de agua      │        │  │
│  │     │                  │  (ANB logo)                 │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Eliminar audio             │        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Guardar video procesado ──────────►│        │  │
│  │     │                  │               │              │        │  │
│  │     │                  │─ Actualizar estado ────────►│        │  │
│  │     │                  │  (status: processed)        │        │  │
│  │     │                  │  + processed_path           │        │  │
│  │     │                  │  + processed_at             │        │  │
│  │     │                  │               │              │        │  │
│  │     │─ Resultado guardado              │              │        │  │
│  │     │                  │               │              │        │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Manejo de Errores:                                                    │
│  ─────────────────────────────────────────────────────────────────     │
│  - Si falla: status = "failed"                                         │
│  - Reintentos automáticos (hasta 3 intentos)                           │
│  - Logging detallado del error                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Votación

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    FLUJO DE VOTACIÓN                                    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  5. VOTACIÓN POR VIDEO                                          │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Usuario                API              BD                     │  │
│  │     │                    │               │                      │  │
│  │     │─ POST /public/videos/{id}/vote    │                      │  │
│  │     │  + JWT token (opcional)            │                      │  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Validar video existe ────────────►│  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Validar status = "processed" ────►│  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Validar voto único ──────────────►│  │
│  │     │                    │  (voter_id, video_id)              │  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Crear registro de voto ──────────►│  │
│  │     │                    │               │                      │  │
│  │     │◄─ 201 Created ────│               │                      │  │
│  │     │  + vote_count      │               │                      │  │
│  │                                                                  │  │
│  │  Restricciones:                                                 │  │
│  │  - Un voto por usuario por video (UNIQUE constraint)            │  │
│  │  - Solo videos procesados pueden recibir votos                  │  │
│  │  - Público general puede votar sin autenticación                │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Ranking

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    FLUJO DE RANKING                                     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  6. OBTENER RANKING                                             │  │
│  │  ─────────────────────────────────────────────────────────────  │  │
│  │                                                                  │  │
│  │  Usuario                API              BD                     │  │
│  │     │                    │               │                      │  │
│  │     │─ GET /public/rankings              │                      │  │
│  │     │  (opcional: ?city=Bogotá)          │                      │  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Consultar videos procesados ──────►│  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Contar votos por video ──────────►│  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Ordenar por votos DESC ──────────►│  │
│  │     │                    │               │                      │  │
│  │     │                    │─ Filtrar por ciudad (si aplica) ──►│  │
│  │     │                    │               │                      │  │
│  │     │◄─ 200 OK ─────────│               │                      │  │
│  │     │  [                 │               │                      │  │
│  │     │    {               │               │                      │  │
│  │     │      video_id,     │               │                      │  │
│  │     │      title,        │               │                      │  │
│  │     │      owner_name,   │               │                      │  │
│  │     │      city,         │               │                      │  │
│  │     │      vote_count,   │               │                      │  │
│  │     │      rank          │               │                      │  │
│  │     │    },              │               │                      │  │
│  │     │    ...             │               │                      │  │
│  │     │  ]                 │               │                      │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
