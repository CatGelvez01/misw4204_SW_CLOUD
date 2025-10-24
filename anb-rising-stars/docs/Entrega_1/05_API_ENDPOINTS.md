# Documentación de API Endpoints - ANB Rising Stars Showcase

## Información General

**Base URL**: `http://localhost:8080/api`

**Autenticación**: JWT Bearer Token (excepto endpoints públicos)

**Formato de Respuesta**: JSON

**Documentación Interactiva**: Disponible en `http://localhost:8080/docs` (Swagger UI)

---

## Autenticación

### 1. Registro de Usuario

**Endpoint**: `POST /auth/signup`

**Descripción**: Registra un nuevo jugador en el sistema.

**Request Body**:
```json
{
  "first_name": "string (1-100 caracteres)",
  "last_name": "string (1-100 caracteres)",
  "email": "string (email válido, único)",
  "password1": "string (mínimo 8 caracteres)",
  "password2": "string (debe coincidir con password1)",
  "city": "string (1-100 caracteres)",
  "country": "string (1-100 caracteres)"
}
```

**Response (201 Created)**:
```json
{
  "message": "Usuario creado exitosamente.",
  "user_id": 1
}
```

**Errores**:
- `400 Bad Request`: Las contraseñas no coinciden o el email ya está registrado
- `422 Unprocessable Entity`: Validación de datos fallida

---

### 2. Autenticación (Login)

**Endpoint**: `POST /auth/login`

**Descripción**: Autentica un usuario y retorna un JWT token.

**Request Body**:
```json
{
  "email": "string (email registrado)",
  "password": "string (contraseña correcta)"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errores**:
- `401 Unauthorized`: Credenciales inválidas

**Uso del Token**:
```
Authorization: Bearer <access_token>
```

---

## Gestión de Videos

### 3. Cargar Video

**Endpoint**: `POST /videos/upload`

**Descripción**: Carga un video para procesamiento.

**Autenticación**: Requerida (JWT)

**Request**:
- `Content-Type`: `multipart/form-data`
- `video_file`: Archivo MP4 (máximo 100MB)
- `title`: Título del video (1-255 caracteres, sin caracteres especiales)

**Response (201 Created)**:
```json
{
  "message": "Video subido correctamente. Procesamiento en curso.",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errores**:
- `400 Bad Request`: Formato inválido, título con caracteres no permitidos
- `401 Unauthorized`: Token inválido o expirado
- `413 Request Entity Too Large`: Archivo excede 100MB

**Validaciones**:
- Solo archivos MP4
- Máximo 100MB
- Título sin caracteres especiales (solo letras, números, espacios, guiones, guiones bajos)

---

### 4. Listar Mis Videos

**Endpoint**: `GET /videos`

**Descripción**: Lista todos los videos cargados por el usuario autenticado.

**Autenticación**: Requerida (JWT)

**Query Parameters**: Ninguno

**Response (200 OK)**:
```json
[
  {
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Mi video de baloncesto",
    "status": "processed",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "processed_at": "2024-01-15T10:35:00Z",
    "processed_url": "http://localhost:8080/processed/550e8400-e29b-41d4-a716-446655440000.mp4",
    "votes": 5
  }
]
```

**Estados de Video**:
- `uploaded`: Video cargado, en espera de procesamiento
- `processing`: Video siendo procesado
- `processed`: Video procesado y listo para votación
- `failed`: Error durante el procesamiento

**Errores**:
- `401 Unauthorized`: Token inválido o expirado

---

### 5. Obtener Detalle de Video

**Endpoint**: `GET /videos/{video_id}`

**Descripción**: Obtiene los detalles de un video específico.

**Autenticación**: Requerida (JWT)

**Path Parameters**:
- `video_id`: UUID del video

**Response (200 OK)**:
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Mi video de baloncesto",
  "status": "processed",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:35:00Z",
  "original_url": "http://localhost:8080/uploads/550e8400-e29b-41d4-a716-446655440000.mp4",
  "processed_url": "http://localhost:8080/processed/550e8400-e29b-41d4-a716-446655440000.mp4",
  "votes": 5
}
```

**Errores**:
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: No tienes permiso para acceder a este video
- `404 Not Found`: El video no existe

---

### 6. Eliminar Video

**Endpoint**: `DELETE /videos/{video_id}`

**Descripción**: Elimina un video cargado por el usuario.

**Autenticación**: Requerida (JWT)

**Path Parameters**:
- `video_id`: UUID del video

**Response (200 OK)**:
```json
{
  "message": "El video ha sido eliminado exitosamente.",
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Restricciones**:
- Solo el propietario del video puede eliminarlo
- No se pueden eliminar videos que ya tienen votos

**Errores**:
- `400 Bad Request`: Video no puede ser eliminado (tiene votos)
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: No tienes permiso para eliminar este video
- `404 Not Found`: El video no existe

---

## Votación y Ranking (Públicos)

### 7. Listar Videos Públicos

**Endpoint**: `GET /public/videos`

**Descripción**: Lista todos los videos disponibles para votación.

**Autenticación**: No requerida

**Query Parameters**: Ninguno

**Response (200 OK)**:
```json
[
  {
    "video_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Mi video de baloncesto",
    "status": "processed",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "processed_at": "2024-01-15T10:35:00Z",
    "processed_url": "http://localhost:8080/processed/550e8400-e29b-41d4-a716-446655440000.mp4",
    "votes": 5
  }
]
```

**Errores**: Ninguno (siempre retorna lista, puede estar vacía)

---

### 8. Votar por Video

**Endpoint**: `POST /public/videos/{video_id}/vote`

**Descripción**: Registra un voto para un video.

**Autenticación**: Requerida (JWT)

**Path Parameters**:
- `video_id`: UUID del video

**Request Body**: Vacío

**Response (200 OK)**:
```json
{
  "message": "Voto registrado exitosamente."
}
```

**Restricciones**:
- Un voto por usuario por video (UNIQUE constraint)
- Solo se pueden votar videos con estado "processed"

**Errores**:
- `400 Bad Request`: Ya has votado por este video
- `401 Unauthorized`: Token inválido o expirado
- `404 Not Found`: El video no existe

---

### 9. Obtener Ranking

**Endpoint**: `GET /public/rankings`

**Descripción**: Obtiene el ranking de jugadores ordenados por votos.

**Autenticación**: No requerida

**Query Parameters**:
- `city` (opcional): Filtrar por ciudad
- `limit` (opcional, default: 100): Número de resultados (1-1000)
- `offset` (opcional, default: 0): Offset para paginación

**Response (200 OK)**:
```json
[
  {
    "position": 1,
    "username": "Juan Pérez",
    "city": "Bogotá",
    "votes": 25
  },
  {
    "position": 2,
    "username": "María García",
    "city": "Medellín",
    "votes": 20
  }
]
```

**Ejemplos de Uso**:
```
GET /public/rankings
GET /public/rankings?city=Bogotá
GET /public/rankings?limit=50&offset=0
GET /public/rankings?city=Bogotá&limit=10&offset=20
```

**Errores**:
- `400 Bad Request`: Parámetros inválidos (limit fuera de rango, offset negativo)

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Autenticación requerida o inválida |
| 403 | Forbidden - Permiso denegado |
| 404 | Not Found - Recurso no encontrado |
| 413 | Request Entity Too Large - Archivo demasiado grande |
| 422 | Unprocessable Entity - Validación de datos fallida |
| 500 | Internal Server Error - Error del servidor |

---

## Estructura de Errores

Todos los errores retornan en el siguiente formato:

```json
{
  "detail": "Descripción del error"
}
```

---

## Autenticación y Seguridad

### JWT Token

- **Algoritmo**: HS256
- **Expiración**: 60 minutos (configurable)
- **Payload**:
  ```json
  {
    "sub": "user_id",
    "email": "user_email",
    "exp": 1234567890
  }
  ```

### Contraseñas

- **Hashing**: bcrypt
- **Mínimo**: 8 caracteres
- **Requisitos**: Sin restricciones adicionales

---

## Ejemplos de Uso con cURL

### Registro
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "password1": "password123",
    "password2": "password123",
    "city": "Bogotá",
    "country": "Colombia"
  }'
```

### Login
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "password123"
  }'
```

### Cargar Video
```bash
curl -X POST http://localhost:8080/api/videos/upload \
  -H "Authorization: Bearer <token>" \
  -F "video_file=@video.mp4" \
  -F "title=Mi video de baloncesto"
```

### Votar
```bash
curl -X POST http://localhost:8080/api/public/videos/550e8400-e29b-41d4-a716-446655440000/vote \
  -H "Authorization: Bearer <token>"
```

### Obtener Ranking
```bash
curl -X GET "http://localhost:8080/api/public/rankings?city=Bogotá&limit=10"
```
