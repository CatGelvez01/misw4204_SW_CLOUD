# Paso 5: Configurar Load Balancer (ALB)

## 1️⃣ CREAR TARGET GROUP

En AWS Console → EC2 → Load Balancing → Target Groups → **Create target group**

**Configuración:**
- **Name**: `anb-web-targets`
- **Protocol**: HTTP
- **Port**: 80
- **VPC**: Tu VPC
- **Health check path**: `/health`
- **Health check protocol**: HTTP
- **Healthy threshold**: 2
- **Unhealthy threshold**: 3
- **Timeout**: 5 seconds
- **Interval**: 30 seconds

Click **Create target group**

---

## 2️⃣ REGISTRAR INSTANCIA EN TARGET GROUP

En el Target Group `anb-web-targets` → **Targets** → **Register targets**

- Selecciona `anb-web-server`
- **Port**: 80
- Click **Register targets**

Espera 1-2 minutos a que la instancia pase a estado **Healthy**

---

## 3️⃣ CREAR APPLICATION LOAD BALANCER

En AWS Console → EC2 → Load Balancing → Load Balancers → **Create load balancer** → **Application Load Balancer**

**Configuración:**
- **Name**: `anb-web-lb`
- **Scheme**: Internet-facing
- **IP address type**: IPv4
- **VPC**: Tu VPC
- **Subnets**: Selecciona al menos 2 subnets públicas en diferentes AZs

**Security Group:**
- Nombre: `anb-web-lb-sg`
- Inbound:
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0 (opcional)

**Listeners and routing:**
- **Protocol**: HTTP
- **Port**: 80
- **Default action**: Forward to `anb-web-targets`

Click **Create load balancer**

---

## 4️⃣ OBTENER DNS DEL ALB

En Load Balancers → `anb-web-lb` → Copia el **DNS name**

Ejemplo: `anb-web-lb-123456789.us-east-1.elb.amazonaws.com`

---

## 5️⃣ ACTUALIZAR CONFIGURACIÓN

En la instancia web, actualiza `.env`:

```bash
SERVER_URL=http://anb-web-lb-123456789.us-east-1.elb.amazonaws.com
CORS_ORIGINS=["http://anb-web-lb-123456789.us-east-1.elb.amazonaws.com"]
```

Reinicia FastAPI:
```bash
sudo systemctl restart anb-backend
```

---

## ✅ VALIDACIÓN

```bash
# Probar health check
curl http://anb-web-lb-123456789.us-east-1.elb.amazonaws.com/health

# Probar root endpoint
curl http://anb-web-lb-123456789.us-east-1.elb.amazonaws.com/
```

Verifica que la instancia esté en estado **Healthy** en Target Groups → Targets
