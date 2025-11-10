# Arquitectura de Despliegue en AWS - Entrega 2

## Descripción General

Este documento describe la arquitectura de la aplicación desplegada en Amazon Web Services (AWS) para la Entrega 2.

## Componentes Principales

### 1. Amazon EC2 - Web Server
- **Descripción**: Instancia de cómputo que ejecuta el servidor web de la aplicación
- **Especificaciones**: t3.small (2 vCPU, 2 GiB RAM, 50 GiB almacenamiento)
- **Software**: FastAPI + Nginx
- **Rol**: Exponer la API REST

### 2. Amazon EC2 - Worker
- **Descripción**: Instancia de cómputo que procesa tareas asincrónicas
- **Especificaciones**: t3.small (2 vCPU, 2 GiB RAM, 50 GiB almacenamiento)
- **Software**: Celery + FFmpeg
- **Rol**: Procesar archivos de forma asincrónica

### 3. Amazon EC2 - File Server
- **Descripción**: Instancia de cómputo con almacenamiento compartido
- **Especificaciones**: t3.small (2 vCPU, 2 GiB RAM, 50 GiB almacenamiento)
- **Software**: NFS Server, Redis, PostgreSQL (temporal)
- **Rol**: Almacenar archivos compartidos y gestionar cola de tareas

### 4. Amazon RDS - PostgreSQL
- **Descripción**: Base de datos relacional administrada
- **Especificaciones**: db.t3.micro (100 GiB almacenamiento)
- **Rol**: Persistencia de datos de la aplicación

## Cambios Respecto a Entrega 1

- Migración de entorno local a AWS
- Separación de componentes en instancias EC2 independientes
- Implementación de NFS para almacenamiento compartido
- Uso de RDS para base de datos administrada

## Diagrama de Despliegue

```mermaid
graph TB
    subgraph AWS["AWS Cloud"]
        subgraph VPC["Default VPC"]
            WEB["EC2: Web Server<br/>FastAPI + Nginx"]
            WORKER["EC2: Worker<br/>Celery + FFmpeg"]
            FILE["EC2: File Server<br/>NFS + Redis"]
            RDS["RDS: PostgreSQL<br/>db.t3.micro"]
        end
    end

    CLIENT["Cliente"]

    CLIENT -->|HTTP/HTTPS| WEB
    WEB -->|NFS| FILE
    WEB -->|Redis| FILE
    WEB -->|PostgreSQL| RDS

    WORKER -->|NFS| FILE
    WORKER -->|Redis| FILE
    WORKER -->|PostgreSQL| RDS

    style WEB fill:#FF9900
    style WORKER fill:#FF9900
    style FILE fill:#FFA500
    style RDS fill:#527FFF
    style AWS fill:#232F3E,color:#fff
    style VPC fill:#E8E8E8,color:#000
```

## Configuración de Seguridad

### Security Groups

```mermaid
graph LR
    subgraph SG["Security Groups"]
        WEB_SG["anb-web-sg<br/>Inbound: SSH, HTTP, HTTPS"]
        WORKER_SG["anb-worker-sg<br/>Inbound: SSH, NFS, Redis"]
        FILE_SG["anb-file-sg<br/>Inbound: SSH, NFS"]
        RDS_SG["anb-rds-sg<br/>Inbound: PostgreSQL"]
    end

    WEB_SG -->|NFS 2049| FILE_SG
    WEB_SG -->|Redis 6379| FILE_SG
    WEB_SG -->|PostgreSQL 5432| RDS_SG

    WORKER_SG -->|NFS 2049| FILE_SG
    WORKER_SG -->|Redis 6379| FILE_SG
    WORKER_SG -->|PostgreSQL 5432| RDS_SG

    style WEB_SG fill:#FFE5CC
    style WORKER_SG fill:#FFE5CC
    style FILE_SG fill:#FFD9B3
    style RDS_SG fill:#CCE5FF
```


## Flujo de Datos

```mermaid
graph TB
    CLIENT["Cliente"]

    CLIENT -->|1. Upload archivo| WEB["Web Server"]
    WEB -->|2. Guardar en NFS| NFS["NFS Storage"]
    WEB -->|3. Crear tarea| REDIS["Redis Queue"]
    WEB -->|4. Registrar en BD| RDS["RDS PostgreSQL"]

    REDIS -->|5. Obtener tarea| WORKER["Worker"]
    NFS -->|6. Leer archivo| WORKER
    WORKER -->|7. Procesar| WORKER
    WORKER -->|8. Guardar resultado| NFS
    WORKER -->|9. Actualizar BD| RDS

    RDS -->|10. Consultar estado| WEB
    NFS -->|11. Descargar archivo| CLIENT

    style CLIENT fill:#E8F4F8
    style WEB fill:#FF9900
    style WORKER fill:#FF9900
    style NFS fill:#FFA500
    style REDIS fill:#DC382D
    style RDS fill:#527FFF
```
