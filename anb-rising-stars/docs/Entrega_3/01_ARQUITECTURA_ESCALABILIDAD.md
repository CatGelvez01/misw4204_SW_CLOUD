# ENTREGA 3 - ARQUITECTURA DE ESCALABILIDAD EN LA CAPA WEB

## Descripción General

Este documento describe la arquitectura de la aplicación web escalable desplegada en AWS, implementando soluciones de autoescalado, balanceo de carga y almacenamiento de objetos para soportar una demanda creciente de usuarios.

## Cambios Principales Respecto a Entrega 2

### Nuevos Componentes Implementados

1. **Load Balancer (ELB/ALB)**
   - Distribución de tráfico entre múltiples instancias EC2
   - Health checks automáticos
   - Sesiones persistentes (sticky sessions) si es requerido

2. **Auto Scaling Group**
   - Escalado automático de instancias web (máximo 3 instancias)
   - Políticas basadas en métricas de CloudWatch
   - Escalado horizontal para distribuir carga

3. **Amazon S3**
   - Migración de almacenamiento de NFS a buckets S3
   - Almacenamiento de videos originales y procesados
   - Configuración de permisos y acceso seguro

4. **CloudWatch Monitoring**
   - Monitoreo de métricas de CPU, memoria y red
   - Alarmas para disparo de políticas de escalado
   - Logs centralizados de la aplicación

## Modelo de Despliegue

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │   ALB   │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼───┐        ┌───▼───┐       ┌───▼───┐
    │ EC2-1 │        │ EC2-2 │       │ EC2-3 │
    │ (Web) │        │ (Web) │       │ (Web) │
    └───┬───┘        └───┬───┘       └───┬───┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐      ┌────▼────┐     ┌────▼────┐
    │   RDS  │      │    S3   │     │  Worker │
    │   DB   │      │ Buckets │     │  (EC2)  │
    └────────┘      └─────────┘     └─────────┘
```

## Componentes de la Arquitectura

### 1. Capa Web (EC2 Auto Scaling)
- **Tipo de Instancia**: t3.small (2 vCPU, 2 GiB RAM, 30 GiB almacenamiento)
- **Cantidad**: 1-3 instancias (escalado automático)
- **Sistema Operativo**: Amazon Linux 2 o Ubuntu
- **Aplicación**: API REST (Flask/Django/Node.js)
- **Puerto**: 5000 (aplicación), 80/443 (ALB)

### 2. Load Balancer (ALB)
- **Tipo**: Application Load Balancer
- **Protocolo**: HTTP/HTTPS
- **Health Check**: Cada 30 segundos
- **Timeout**: 60 segundos
- **Distribución**: Round-robin

### 3. Base de Datos (RDS)
- **Motor**: PostgreSQL/MySQL
- **Tipo de Instancia**: db.t3.micro
- **Almacenamiento**: 100 GB (gp2)
- **Backup**: Habilitado
- **Multi-AZ**: Según disponibilidad

### 4. Almacenamiento de Objetos (S3)
- **Bucket**: `anb-rising-stars-videos`
- **Estructura**:
  - `/original/` - Videos originales
  - `/processed/` - Videos procesados
- **Versionado**: Habilitado
- **Acceso**: IAM Role para EC2

### 5. Capa Worker (EC2)
- **Tipo de Instancia**: t3.small
- **Cantidad**: 1 instancia
- **Función**: Procesamiento asíncrono de videos
- **Cola**: SQS o Celery con Redis

### 6. Monitoreo (CloudWatch)
- **Métricas**: CPU, Memoria, Disco, Red
- **Logs**: Centralizados en CloudWatch Logs
- **Alarmas**: Para disparo de escalado

## Políticas de Auto Scaling

### Escala Hacia Arriba (Scale Out)
- **Métrica**: CPU > 70% durante 2 minutos
- **Acción**: Agregar 1 instancia
- **Máximo**: 3 instancias

### Escala Hacia Abajo (Scale In)
- **Métrica**: CPU < 30% durante 5 minutos
- **Acción**: Remover 1 instancia
- **Mínimo**: 1 instancia

## Configuración de Seguridad

### Security Groups
- **Web SG**: Permite 80, 443 desde ALB
- **ALB SG**: Permite 80, 443 desde Internet
- **RDS SG**: Permite puerto 5432/3306 desde Web SG
- **Worker SG**: Permite comunicación interna

### IAM Roles
- **LabRole**: Asignado a todas las instancias EC2
- **Permisos**: S3, RDS, CloudWatch, SQS

## Cambios en la Aplicación

1. **Configuración de S3**: Integración de SDK de AWS
2. **Variables de Entorno**: Credenciales y endpoints
3. **Health Check Endpoint**: `/health` para ALB
4. **Stateless**: Aplicación sin estado local
5. **Logs**: Enviados a CloudWatch

## Consideraciones de Escalabilidad

- Máximo 9 instancias EC2 simultáneas (límite AWS Academy)
- Máximo 32 vCPUs totales
- Almacenamiento EBS limitado a 100 GB
- Monitoreo continuo de costos
- Detener instancias cuando no se usen

## Próximos Pasos

1. Implementar políticas de escalado más sofisticadas
2. Agregar caché (ElastiCache)
3. Implementar CDN (CloudFront)
4. Optimizar costos con instancias reservadas
5. Implementar disaster recovery
