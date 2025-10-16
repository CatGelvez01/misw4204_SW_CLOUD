# 🚀 Inicio Rápido - ANB Rising Stars Showcase

## ⚡ En 5 Minutos

### Requisito
- Docker y Docker Compose

### Pasos

```bash
# 1. Clonar
git clone <repository-url>
cd anb-rising-stars

# 2. Iniciar
docker compose up -d

# 3. Verificar
docker compose ps

# 4. Acceder
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

---

## 📝 Primeros Pasos con la API

### 1️⃣ Registrar Usuario

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "password1": "Password123!",
    "password2": "Password123!",
    "city": "Bogotá",
    "country": "Colombia"
  }'
```

**Respuesta:**
```json
{"message": "Usuario creado exitosamente.", "user_id": 1}
```

### 2️⃣ Iniciar Sesión

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "Password123!"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Guardar el token para los siguientes requests.**

### 3️⃣ Subir Video

```bash
curl -X POST http://localhost:8000/api/videos/upload \
  -H "Authorization: Bearer <TOKEN>" \
  -F "video_file=@video.mp4" \
  -F "title=Mi mejor tiro de 3"
```

### 4️⃣ Ver Videos Públicos

```bash
curl http://localhost:8000/api/public/videos
```

### 5️⃣ Votar

```bash
curl -X POST http://localhost:8000/api/public/videos/1/vote \
  -H "Authorization: Bearer <TOKEN>"
```

### 6️⃣ Ver Ranking

```bash
curl http://localhost:8000/api/public/rankings
```

---

## 💻 Desarrollo Local

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

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| Servicios no inician | `docker compose logs` |
| Reconstruir | `docker compose up -d --build` |
| Limpiar todo | `docker compose down -v` |
| Ver estado | `docker compose ps` |

---

## 📚 Más Información

- **[README.md](/anb-rising-stars/README.md)** - Descripción general
- **[docs/ARCHITECTURE.md](/anb-rising-stars/docs/ARCHITECTURE.md)** - Arquitectura
- **[docs/DEVELOPMENT.md](/anb-rising-stars/docs/DEVELOPMENT.md)** - Desarrollo
- **[docs/API_ENDPOINTS.md](/anb-rising-stars/docs/API_ENDPOINTS.md)** - Endpoints

---

**¡Listo!** 🎉 Accede a http://localhost:8000/docs para explorar la API.
