# ANB Rising Stars Showcase - Entrega No. 1

## Información del Equipo

| Nombre | Correo Uniandes |
|--------|-----------------|
| Integrante 1 | correo1@uniandes.edu.co |
| Integrante 2 | correo2@uniandes.edu.co |
| Integrante 3 | correo3@uniandes.edu.co |
| Integrante 4 | correo4@uniandes.edu.co |
| Integrante 5 | correo5@uniandes.edu.co |

---

## Documentación de la Entrega

Toda la documentación se encuentra en [/anb-rising-stars/docs/Entrega_1/](anb-rising-stars/docs/Entrega_1/).

| Documento | Descripción |
|-----------|-------------|
| **[01_MODELO_DATOS.md](anb-rising-stars/docs/Entrega_1/01_MODELO_DATOS.md)** | Diagrama Entidad-Relación (ERD) y especificación detallada de entidades, atributos y relaciones |
| **[02_ARQUITECTURA.md](anb-rising-stars/docs/Entrega_1/02_ARQUITECTURA.md)** | Diagramas C4, decisiones de diseño y patrones arquitectónicos |
| **[03_DIAGRAMA_COMPONENTES.md](anb-rising-stars/docs/Entrega_1/03_DIAGRAMA_COMPONENTES.md)** | Representación de backend (FastAPI), worker (Celery), message broker (Redis/RabbitMQ) y base de datos (PostgreSQL) |
| **[04_FLUJO_PROCESOS.md](anb-rising-stars/docs/Entrega_1/04_FLUJO_PROCESOS.md)** | Diagrama de flujo detallado de las etapas de carga, procesamiento y entrega de archivos |
| **[05_API_ENDPOINTS.md](anb-rising-stars/docs/Entrega_1/05_API_ENDPOINTS.md)** | Contrato OpenAPI, especificación de endpoints, códigos HTTP, validación y manejo de errores |
| **[06_DESPLIEGUE.md](anb-rising-stars/docs/Entrega_1/06_DESPLIEGUE.md)** | Infraestructura de ejecución, configuración Docker Compose y guía reproducible para replicar el entorno |
| **[07_SONARQUBE.md](anb-rising-stars/docs/Entrega_1/07_SONARQUBE.md)** | Reporte de calidad: bugs, vulnerabilidades, code smells, cobertura de pruebas, duplicación de código y quality gate |


---

## Colecciones de Postman

Las colecciones de Postman se encuentran en [/anb-rising-stars/collections/postman_environment.json](anb-rising-stars/collections/postman_environment.json) en formato JSON.

---

## Video de Sustentación

El enlace al video de sustentación se encuentra en [/anb-rising-stars/sustentacion/Entrega_1/video.mp4](anb-rising-stars/sustentacion/Entrega_1/video.mp4).

---

# Proyecto ANB Rising Stars

Este proyecto forma parte del curso **MISW4204 - Software en la Nube**, e implementa una aplicación web basada en arquitectura de microservicios, contenedores y base de datos SQL. Incluye API REST con autenticación, procesamiento asíncrono con Celery y despliegue con Docker Compose.

---

## 📦 Requerimientos del Sistema

- **Python:** 3.10 o superior  
- **SQL Database:** PostgreSQL 14 o superior  
- **Docker:** 24+  
- **Docker Compose:** 2.20+  

---

## 🧰 Instalación de dependencias

Antes de ejecutar el proyecto, crea un entorno virtual e instala los requerimientos.

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # En Linux/Mac
venv\Scripts\activate      # En Windows

# Instalar dependencias
pip install -r requirements.txt


## Análisis de Capacidad

El plan de análisis de capacidad de la aplicación se encuentra en [/anb-rising-stars/capacity-planning/plan_de_pruebas.md](anb-rising-stars/capacity-planning/plan_de_pruebas.md). Este documento incluye el plan detallado de análisis de capacidad, los escenarios de carga planteados, las métricas seleccionadas, los resultados esperados y las recomendaciones para escalar la solución.
