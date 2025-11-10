# Paso 1: Crear 3 EC2s en AWS

## Requisitos Previos
- Cuenta AWS activa
- Acceso a AWS Console (https://console.aws.amazon.com)

---

## 1️⃣ CREAR PRIMERA EC2: WEB SERVER

### En AWS Console:
1. Ve a **EC2 Dashboard** → **Instances** → **Launch Instances**

### Configuración:
- **Name**: `anb-web-server`
- **AMI**: Ubuntu 22.04 LTS (busca "Ubuntu 22.04")
- **Instance Type**: `t3.small` (2 vCPU, 2 GiB RAM)
- **Key Pair**: Crea una nueva o usa existente (guarda el `.pem`)
- **Network**: Default VPC
- **Security Group**: Crea uno nuevo llamado `anb-web-sg`
  - Inbound Rules:
    - SSH (22): Desde tu IP
    - HTTP (80): Desde 0.0.0.0/0
    - HTTPS (443): Desde 0.0.0.0/0
    - All traffic: Desde 0.0.0.0/0
- **Storage**: 50 GiB (gp3)
- **Launch**

### Después de crear:
- Anota la **IP Pública Elástica** (o asigna una)
- Anota el **DNS público**

---

## 2️⃣ CREAR SEGUNDA EC2: WORKER

### En AWS Console:
1. Ve a **EC2 Dashboard** → **Instances** → **Launch Instances**

### Configuración:
- **Name**: `anb-worker`
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: `t3.small`
- **Key Pair**: Usa la misma del paso anterior
- **Network**: Default VPC
- **Security Group**: Crea uno nuevo llamado `anb-worker-sg`
  - Inbound Rules:
    - SSH (22): Desde tu IP
    - NFS (2049): Type "NFS", Source: `anb-web-sg`
    - Custom TCP (6379): Type "Custom TCP", Port 6379, Source: `anb-web-sg`
    - All traffic: Desde 0.0.0.0/0
- **Storage**: 50 GiB (gp3)
- **Launch**

### Después de crear:
- Anota la **IP Privada** (ej: 172.31.x.x)

---

## 3️⃣ CREAR TERCERA EC2: FILE SERVER (NFS)

### En AWS Console:
1. Ve a **EC2 Dashboard** → **Instances** → **Launch Instances**

### Configuración:
- **Name**: `anb-file-server`
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: `t3.small`
- **Key Pair**: Usa la misma
- **Network**: Default VPC
- **Security Group**: Crea uno nuevo llamado `anb-file-sg`
  - Inbound Rules (agregar 3 reglas):
    - Regla 1: SSH (22) - Source: tu IP
    - Regla 2: NFS (2049) - Source: `anb-web-sg`
    - Regla 3: NFS (2049) - Source: `anb-worker-sg`
    - All traffic: Desde 0.0.0.0/0
- **Storage**: 50 GiB (gp3)
- **Launch**

### Después de crear:
- Anota la **IP Privada** (ej: 172.31.x.x)



## ✅ VALIDACIÓN

Después de crear todo, verifica:
- [ ] 3 EC2s en estado "running"
- [ ] Puedes hacer SSH a Web Server: `ssh -i tu-key.pem ubuntu@<web-server-ip>`
- [ ] Puedes hacer SSH a Worker: `ssh -i tu-key.pem ubuntu@<worker-ip>` (desde Web Server)
- [ ] Puedes hacer SSH a File Server: `ssh -i tu-key.pem ubuntu@<file-server-ip>` (desde Web Server)

---

## 🚨 IMPORTANTE

- **Guarda el archivo .pem** en un lugar seguro
- **Anota todos los IPs y endpoints** (los necesitarás en Paso 2)
