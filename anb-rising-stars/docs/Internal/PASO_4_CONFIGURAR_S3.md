# Paso 4: Crear y Configurar S3


## 1️⃣ CREAR BUCKET S3

### En AWS Console:
1. Ve a **S3** → **Buckets** → **Create bucket**

### Configuración:
- **Bucket name**: `anb-rising-stars-videos`
- **Region**: `us-east-1`
- **Block Public Access**: Dejar por defecto (bloqueado)
- **Create bucket**

### Después de crear:
- Anota el **nombre del bucket**: `anb-rising-stars-videos`

---

## 2️⃣ CONFIGURAR VARIABLES DE ENTORNO

En `.env`:

```bash
USE_S3=True
AWS_REGION=us-east-1
S3_BUCKET=anb-rising-stars-videos
```
