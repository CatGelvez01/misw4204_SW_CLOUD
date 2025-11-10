# Paso 3: Configurar PostgreSQL en AWS RDS

## 1️⃣ CREAR INSTANCIA RDS

### En AWS Console:
1. Ve a **RDS Dashboard** → **Create Database**

### Configuración:
- **Engine**: PostgreSQL
- **Version**: 16.x
- **DB instance identifier**: `anb-rising-stars`
- **Master username**: `anb_user`
- **Master password**: `anb_password`
- **DB name**: `anb_rising_stars`
- **Instance class**: `db.t3.micro` (desarrollo)
- **Storage**: 100 GiB (gp2)
- **VPC**: Default VPC
- **Security Group**: Crear nuevo `anb-rds-sg`
  - Inbound Rule: PostgreSQL (5432) desde `anb-web-sg` y `anb-worker-sg`
- **Backup retention**: 0 days (minimizar costos)
- **Multi-AZ**: NO
- **Create Database**

### Después de crear:
- Anota el **Endpoint** (ej: `anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com`)

---

## 2️⃣ ACTUALIZAR WEB SERVER

```bash
ssh -i tu-key.pem ubuntu@<web-server-ip>
cd /home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars

# Actualizar .env con el endpoint de RDS
sed -i 's|postgresql://anb_user:anb_password@[^:]*:5432|postgresql://anb_user:anb_password@anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com:5432|g' .env
# ó
DATABASE_URL=postgresql://anb_user:anb_password@anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com:5432/anb_rising_stars

# Verificar
cat .env | grep DATABASE_URL

# Reiniciar servicio
sudo systemctl restart anb-backend.service
sudo systemctl status anb-backend.service
```

---

## 3️⃣ ACTUALIZAR WORKER

```bash
ssh -i tu-key.pem ubuntu@<worker-ip>
cd /home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars

# Actualizar .env con el endpoint de RDS
sed -i 's|postgresql://anb_user:anb_password@[^:]*:5432|postgresql://anb_user:anb_password@anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com:5432|g' .env

# Verificar
cat .env | grep DATABASE_URL

# Reiniciar servicio
sudo systemctl restart anb-celery-worker.service
sudo systemctl status anb-celery-worker.service
```

---

## ✅ VALIDACIÓN

```bash
# Desde Web Server
psql -h anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com -U anb_user -d anb_rising_stars -c "SELECT 1"

# Desde tu máquina
curl http://<web-server-ip>/
```

---

## 🚨 IMPORTANTE

- Reemplaza `anb-rising-stars.xxxxx.us-east-1.rds.amazonaws.com` con tu endpoint real
- Asegúrate que el security group de RDS permite tráfico desde `anb-web-sg` y `anb-worker-sg`
- **Al finalizar la entrega, elimina la instancia RDS** (genera costos altos)
