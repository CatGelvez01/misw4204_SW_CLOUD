# Paso 6: Configurar Auto Scaling

## ⚠️ LIMITACIONES AWS ACADEMY

- **Máximo 9 instancias EC2 simultáneas** (todas las regiones)
- **Máximo 32 vCPUs totales** en ejecución
- **Máximo 3 instancias web** (según requisitos del proyecto)
- **Tipos permitidos**: nano, micro, small, medium, large
- **Solo instancias bajo demanda** (no spot, no reservadas)

---

## 1️⃣ CREAR AMI DE LA INSTANCIA WEB

En AWS Console → EC2 → Instances

1. Selecciona `anb-web-server`
2. **Image and templates** → **Create image**
3. **Image name**: `anb-web-server-ami`
4. **Image description**: "ANB Web Server with Nginx and FastAPI"
5. Click **Create image**

Espera a que el estado sea **Available** (5-10 minutos)

---

## 2️⃣ CREAR LAUNCH TEMPLATE

En AWS Console → EC2 → Launch Templates → **Create launch template**

**Configuración:**
- **Launch template name**: `anb-web-template`
- **AMI**: Selecciona `anb-web-server-ami` (la que creaste)
- **Instance type**: `t3.small`
- **Key pair**: Tu key pair
- **Security groups**: `anb-web-sg`
- **Storage**: 30 GiB (gp3)

Click **Create launch template**

---

## 3️⃣ CREAR AUTO SCALING GROUP

En AWS Console → EC2 → Auto Scaling Groups → **Create Auto Scaling group**

**Paso 1 - Configuración básica:**
- **Auto Scaling group name**: `anb-web-asg`
- **Launch template**: `anb-web-template`
- Click **Next**

**Paso 2 - Network:**
- **VPC**: Tu VPC
- **Subnets**: Selecciona al menos 2 subnets públicas en diferentes AZs
- Click **Next**

**Paso 3 - Load balancer:**
- **Attach to an existing load balancer**: Selecciona esta opción
- **Choose from your existing load balancers**: `anb-web-lb`
- **Choose from your existing target groups**: `anb-web-targets`
- Click **Next**

**Paso 4 - Tamaño del grupo:**
- **Desired capacity**: 1
- **Minimum capacity**: 1
- **Maximum capacity**: 3
- Click **Next**

**Paso 5 - Políticas de escalado:**
- **Scaling policies**: Target tracking scaling policy
- **Metric type**: Average CPU Utilization
- **Target value**: 70
- Click **Next**

**Paso 6 - Notificaciones:**
- Opcional (puedes saltarlo)
- Click **Next**

**Paso 7 - Revisar:**
- Verifica la configuración
- Click **Create Auto Scaling group**

---

## 4️⃣ VERIFICAR AUTO SCALING GROUP

En AWS Console → EC2 → Auto Scaling Groups → `anb-web-asg`

Verifica:
- **Desired capacity**: 1
- **Current instances**: 1
- **Min**: 1
- **Max**: 3
- **Scaling policies**: Target tracking (CPU 70%)

---

## 5️⃣ ACTUALIZAR SECURITY GROUP DE LA INSTANCIA

La instancia web debe permitir tráfico desde el ALB.

En AWS Console → EC2 → Security Groups → `anb-web-sg`

**Inbound rules:**
- **Type**: HTTP
- **Protocol**: TCP
- **Port**: 80
- **Source**: `anb-web-lb-sg` (security group del ALB)

---

## ✅ VALIDACIÓN

```bash
# Verificar que el ALB sigue funcionando
curl http://anb-web-lb-123456789.us-east-1.elb.amazonaws.com/health

# Verificar que la instancia está en el Target Group
# AWS Console → Target Groups → anb-web-targets → Targets
# Debe mostrar 1 instancia en estado "Healthy"
```

**En AWS Console:**
- Auto Scaling Groups → `anb-web-asg` → Activity
- Verifica que la instancia fue lanzada por el ASG

---

## 📝 NOTAS

- El ASG mantendrá siempre 1 instancia corriendo (desired capacity)
- Si CPU > 70%, escalará a 2 instancias
- Si CPU > 70% nuevamente, escalará a 3 instancias (máximo)
- Si CPU < 70%, bajará a 2 instancias
- Si CPU < 70% nuevamente, bajará a 1 instancia (mínimo)
- El ALB distribuirá tráfico entre todas las instancias "Healthy"

---

## ⚠️ IMPORTANTE

- **Detén las instancias cuando no las uses** para ahorrar créditos
- El ASG las reiniciará automáticamente cuando las necesites
- Verifica que no superes 9 instancias simultáneas
- Verifica que no superes 32 vCPUs totales
