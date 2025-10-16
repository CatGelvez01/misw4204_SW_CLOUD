# Especificación de Endpoints API - ANB Rising Stars Showcase

## Base URL
```
http://localhost:8000/api
```

## Documentación Interactiva

**Recomendamos usar Swagger para explorar los endpoints con ejemplos en vivo:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Autenticación
Todos los endpoints que requieren autenticación deben incluir el header:
```
Authorization: Bearer <token_jwt>
```

---

## 1. Autenticación

### 1.1 Registro de Jugadores
**Endpoint**: `POST /auth/signup`

**Descripción**: Registrar un nuevo jugador en la plataforma.

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password1": "StrongPass123",
  "password2": "StrongPass123",
  "city": "Bogotá",
  "country": "Colombia"
}
```

**Response** (201 Created):
```json
{
  "message": "Usuario creado exitosamente.",
  "user_id": 1
}
```

**Error Responses**:
- `400 Bad Request`: Email duplicado o contraseñas no coinciden
- `422 Unprocessable Entity`: Validación de datos fallida

---

### 1.2 Inicio de Sesión
**Endpoint**: `POST /auth/login`

**Descripción**: Autenticar usuario y obtener token JWT.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "StrongPass123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Error Responses**:
- `401 Unauthorized`: Credenciales inválidas

---

## 2. Gestión de Videos

### 2.1 Subir Video
**Endpoint**: `POST /videos/upload`

**Autenticación**: Requerida (JWT)

**Descripción**: Subir un video para procesamiento.

**Request** (form-data):
- `video_file` (file, required): Archivo MP4, máximo 100MB
- `title` (string, required): Título descriptivo del video

**Response** (201 Created):
```json
{
  "message": "Video subido correctamente. Procesamiento en curso.",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:
- `400 Bad Request`: Archivo inválido o tamaño excedido
- `401 Unauthorized`: No autenticado

---

### 2.2 Listar Mis Videos
**Endpoint**: `GET /videos`

**Autenticación**: Requerida (JWT)

**Descripción**: Obtener lista de videos del usuario autenticado.

**Query Parameters**:
- `skip` (integer, optional): Número de registros a saltar (default: 0)
- `limit` (integer, optional): Número máximo de registros (default: 100)

**Response** (200 OK):
```json
[
  {
    "video_id": 1,
    "title": "Mi mejor tiro de 3",
    "status": "processed",
    "uploaded_at": "2025-03-10T14:30:00Z",
    "processed_at": "2025-03-10T14:35:00Z",
    "processed_url": "https://anb.com/videos/processed/1.mp4",
    "votes": 125
  },
  {
    "video_id": 2,
    "title": "Habilidades de dribleo",
    "status": "uploaded",
    "uploaded_at": "2025-03-11T10:15:00Z",
    "processed_at": null,
    "processed_url": null,
    "votes": 0
  }
]
```

**Error Responses**:
- `401 Unauthorized`: No autenticado

---

### 2.3 Obtener Detalle de Video
**Endpoint**: `GET /videos/{video_id}`

**Autenticación**: Requerida (JWT)

**Descripción**: Obtener detalles de un video específico.

**Path Parameters**:
- `video_id` (integer, required): ID del video

**Response** (200 OK):
```json
{
  "video_id": 1,
  "title": "Tiros de tres en movimiento",
  "status": "processed",
  "uploaded_at": "2025-03-15T14:22:00Z",
  "processed_at": "2025-03-15T15:10:00Z",
  "original_url": "https://anb.com/uploads/1.mp4",
  "processed_url": "https://anb.com/processed/1.mp4",
  "votes": 125
}
```

**Error Responses**:
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No tienes permiso para acceder a este video
- `404 Not Found`: Video no existe

---

### 2.4 Eliminar Video
**Endpoint**: `DELETE /videos/{video_id}`

**Autenticación**: Requerida (JWT)

**Descripción**: Eliminar un video (solo si no está publicado).

**Path Parameters**:
- `video_id` (integer, required): ID del video

**Response** (200 OK):
```json
{
  "message": "El video ha sido eliminado exitosamente.",
  "video_id": 1
}
```

**Error Responses**:
- `400 Bad Request`: Video no puede ser eliminado
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No tienes permiso
- `404 Not Found`: Video no existe

---

## 3. Votación

### 3.1 Listar Videos Públicos
**Endpoint**: `GET /public/videos`

**Autenticación**: Opcional

**Descripción**: Obtener lista de videos disponibles para votación.

**Query Parameters**:
- `city` (string, optional): Filtrar por ciudad
- `skip` (integer, optional): Número de registros a saltar
- `limit` (integer, optional): Número máximo de registros

**Response** (200 OK):
```json
[
  {
    "video_id": 1,
    "title": "Mi mejor tiro de 3",
    "owner": "John Doe",
    "city": "Bogotá",
    "votes": 125,
    "processed_url": "https://anb.com/videos/processed/1.mp4"
  }
]
```

---

### 3.2 Votar por un Video
**Endpoint**: `POST /public/videos/{video_id}/vote`

**Autenticación**: Requerida (JWT)

**Descripción**: Emitir un voto por un video.

**Path Parameters**:
- `video_id` (integer, required): ID del video

**Response** (200 OK):
```json
{
  "message": "Voto registrado exitosamente."
}
```

**Error Responses**:
- `400 Bad Request`: Ya has votado por este video
- `401 Unauthorized`: No autenticado
- `404 Not Found`: Video no existe

---

## 4. Rankings

### 4.1 Obtener Ranking
**Endpoint**: `GET /public/rankings`

**Autenticación**: Opcional

**Descripción**: Obtener ranking de jugadores por votos.

**Query Parameters**:
- `city` (string, optional): Filtrar por ciudad
- `limit` (integer, optional): Número máximo de resultados (default: 100)
- `offset` (integer, optional): Offset para paginación (default: 0)

**Response** (200 OK):
```json
[
  {
    "position": 1,
    "username": "John Doe",
    "city": "Bogotá",
    "votes": 1530
  },
  {
    "position": 2,
    "username": "Jane Smith",
    "city": "Bogotá",
    "votes": 1495
  }
]
```

**Error Responses**:
- `400 Bad Request`: Parámetro inválido

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Solicitud inválida |
| 401 | Unauthorized - Autenticación requerida |
| 403 | Forbidden - Acceso denegado |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación fallida |
| 500 | Internal Server Error - Error del servidor |

---

## Notas Importantes

### Respuestas de Error

Todos los endpoints retornan respuestas de error estructuradas:

```json
{
  "detail": "Descripción del error"
}
```

### Ejemplos en Swagger

Cada endpoint incluye ejemplos de request y response en Swagger. Los ejemplos muestran:
- Estructura de datos esperada
- Valores de ejemplo
- Códigos de estado HTTP

### Colección de Postman

Próximamente estará disponible una colección de Postman en la carpeta `collections/` para facilitar el testing de endpoints.
