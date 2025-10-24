# Arquitectura de Despliegue en AWS - Entrega 2

## Descripción General

Este documento describe la arquitectura de la aplicación desplegada en Amazon Web Services (AWS) para la Entrega 2.

## Componentes Principales

### 1. Amazon EC2 - Web Server
- **Descripción**: Instancia de cómputo que ejecuta el servidor web de la aplicación
- **Especificaciones**: 2 vCPU, 2 GiB RAM, 50 GiB almacenamiento
- **Rol**: Exponer la API REST

### 2. Amazon EC2 - Worker
- **Descripción**: Instancia de cómputo que procesa archivos
- **Especificaciones**: 2 vCPU, 2 GiB RAM, 50 GiB almacenamiento
- **Rol**: Procesar tareas asincrónicas

### 3. Amazon EC2 - File Server (NFS)
- **Descripción**: Instancia de cómputo con sistema de archivos de red
- **Especificaciones**: 2 vCPU, 2 GiB RAM, 50 GiB almacenamiento
- **Rol**: Almacenar archivos originales y procesados

### 4. Amazon RDS
- **Descripción**: Base de datos relacional administrada
- **Rol**: Persistencia de datos de la aplicación

## Cambios Respecto a Entrega 1

- Migración de entorno local a AWS
- Separación de componentes en instancias EC2 independientes
- Implementación de NFS para almacenamiento compartido
- Uso de RDS para base de datos administrada

## Diagrama de Despliegue

(Por completar con diagrama visual)

## Configuración de Seguridad

(Por completar)

## Consideraciones de Rendimiento

(Por completar)
