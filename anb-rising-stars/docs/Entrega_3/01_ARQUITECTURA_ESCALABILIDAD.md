# ENTREGA 3 - ARQUITECTURA DE ESCALABILIDAD EN LA CAPA WEB

## Cambios Principales

1. **Load Balancer (ALB)**: Distribución de tráfico entre instancias web
2. **Auto Scaling Group**: 1-3 instancias web según demanda
3. **Amazon S3**: Reemplaza NFS para almacenamiento de videos
4. **CloudWatch**: Monitoreo y alarmas de escalado

## Modelo de Despliegue

```mermaid
graph TB
    subgraph AWS["AWS Cloud"]
        subgraph VPC["Default VPC"]
            ALB["ALB<br/>HTTP/HTTPS"]

            subgraph ASG["Auto Scaling Group"]
                WEB1["EC2: Web-1<br/>FastAPI + Nginx"]
                WEB2["EC2: Web-2<br/>FastAPI + Nginx"]
                WEB3["EC2: Web-3<br/>FastAPI + Nginx"]
            end

            FILE["EC2: File Server<br/>Redis"]
            WORKER["EC2: Worker<br/>Celery + FFmpeg"]
            RDS["RDS: PostgreSQL<br/>db.t3.micro"]
            S3["S3: Buckets<br/>Videos"]
        end
    end

    CLIENT["Cliente"]

    CLIENT -->|HTTP/HTTPS| ALB
    ALB -->|Distribuye| WEB1
    ALB -->|Distribuye| WEB2
    ALB -->|Distribuye| WEB3

    WEB1 -->|Redis| FILE
    WEB2 -->|Redis| FILE
    WEB3 -->|Redis| FILE

    WEB1 -->|S3| S3
    WEB2 -->|S3| S3
    WEB3 -->|S3| S3

    WEB1 -->|PostgreSQL| RDS
    WEB2 -->|PostgreSQL| RDS
    WEB3 -->|PostgreSQL| RDS

    WORKER -->|Redis| FILE
    WORKER -->|S3| S3
    WORKER -->|PostgreSQL| RDS

    style ALB fill:#FF9900
    style WEB1 fill:#FF9900
    style WEB2 fill:#FF9900
    style WEB3 fill:#FF9900
    style FILE fill:#FFA500
    style WORKER fill:#FF9900
    style RDS fill:#527FFF
    style S3 fill:#569A31
    style AWS fill:#232F3E,color:#fff
    style VPC fill:#E8E8E8,color:#000
    style ASG fill:#F0F0F0,color:#000
```

## Componentes

| Componente | Especificación |
|-----------|----------------|
| **ALB** | HTTP/HTTPS, health check 30s |
| **Web (ASG)** | t3.small, 1-3 instancias, FastAPI + Nginx |
| **File Server** | t3.small, Redis |
| **RDS** | PostgreSQL db.t3.micro, 100 GB |
| **S3** | Buckets `/original/` y `/processed/` |
| **Worker** | t3.small, Celery + FFmpeg |
| **CloudWatch** | Métricas, logs, alarmas |

## Auto Scaling

| Acción | Métrica | Límite |
|--------|---------|--------|
| Scale Out | CPU > 70% (2 min) | Máx 3 instancias |
| Scale In | CPU < 30% (5 min) | Mín 1 instancia |

## Seguridad

| SG | Puertos | Origen |
|----|---------|--------|
| ALB | 80, 443 | Internet |
| Web | 80, 443 | ALB |
| File Server | 6379 | Web, Worker |
| RDS | 5432 | Web, Worker |
| Worker | Interno | VPC |

**IAM**: LabRole con permisos S3, RDS, CloudWatch

## Límites AWS Academy

- Máx 9 instancias EC2
- Máx 32 vCPUs
- Máx 100 GB EBS
