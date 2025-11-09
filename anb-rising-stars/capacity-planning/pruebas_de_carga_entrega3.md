# PRUEBAS DE CARGA - ENTREGA 3
## Análisis de Capacidad y Escalabilidad

**Fecha de Ejecución**: [Completar con fecha de pruebas]
**Responsables**: [Completar con nombres del equipo]
**Versión**: 1.0

---

## 1. Introducción

Este documento presenta el análisis detallado de las pruebas de carga realizadas en la Entrega 3, evaluando la capacidad de escalabilidad de la aplicación web desplegada en AWS con implementación de Load Balancer, Auto Scaling y almacenamiento en S3.

## 2. Objetivos de las Pruebas

- Validar el funcionamiento del Load Balancer en distribución de tráfico
- Evaluar las políticas de Auto Scaling bajo diferentes cargas
- Medir el rendimiento de la aplicación con múltiples instancias
- Identificar cuellos de botella en la arquitectura
- Determinar la capacidad máxima de usuarios concurrentes
- Validar la integración con S3 bajo carga

## 3. Escenarios de Prueba

### Escenario 1: Carga Progresiva (Ramp-up)

**Objetivo**: Evaluar el comportamiento del sistema bajo aumento gradual de usuarios

**Configuración**:
- Usuarios iniciales: 10
- Incremento: 10 usuarios cada 2 minutos
- Usuarios máximos: 100
- Duración total: 20 minutos
- Endpoints probados: GET /videos, POST /upload, GET /health

**Métricas a Recolectar**:
- Tiempo de respuesta promedio
- Percentil 95 y 99 de latencia
- Tasa de error (%)
- Throughput (req/s)
- CPU de instancias
- Número de instancias activas
- Tiempo de escalado

**Criterios de Éxito**:
- Tiempo de respuesta < 2 segundos (p95)
- Tasa de error < 1%
- Escalado automático en < 3 minutos
- Máximo 3 instancias activas

### Escenario 2: Carga Sostenida (Steady State)

**Objetivo**: Evaluar la estabilidad del sistema bajo carga constante

**Configuración**:
- Usuarios concurrentes: 50
- Duración: 30 minutos
- Mix de operaciones:
  - 40% GET /videos
  - 30% POST /upload (con video pequeño)
  - 20% GET /video/{id}
  - 10% DELETE /video/{id}

**Métricas a Recolectar**:
- Tiempo de respuesta promedio y desviación estándar
- Percentiles de latencia (p50, p95, p99)
- Tasa de error
- Throughput sostenido
- Utilización de recursos (CPU, memoria, disco)
- Comportamiento de Auto Scaling
- Latencia de S3

**Criterios de Éxito**:
- Tiempo de respuesta estable
- Tasa de error < 0.5%
- Número de instancias estable (1-2)
- Sin degradación de rendimiento

## 4. Herramientas de Prueba

- **Apache JMeter**: Generación de carga y recolección de métricas
- **CloudWatch**: Monitoreo de instancias y servicios AWS
- **AWS CLI**: Verificación de estado de Auto Scaling
- **Custom Scripts**: Análisis de logs y generación de reportes

## 5. Resultados Esperados

### Escenario 1 - Carga Progresiva

| Métrica | Esperado | Observado | Estado |
|---------|----------|-----------|--------|
| Tiempo Respuesta (p95) | < 2s | | |
| Tasa Error | < 1% | | |
| Instancias Activas (máx) | 3 | | |
| Tiempo Escalado | < 3 min | | |

### Escenario 2 - Carga Sostenida

| Métrica | Esperado | Observado | Estado |
|---------|----------|-----------|--------|
| Tiempo Respuesta Promedio | < 1s | | |
| Tasa Error | < 0.5% | | |
| Instancias Activas | 1-2 | | |
| Variación Latencia | < 10% | | |

## 6. Análisis de Resultados

### Escenario 1 - Análisis

[Completar con análisis de resultados]

### Escenario 2 - Análisis

[Completar con análisis de resultados]

## 7. Identificación de Cuellos de Botella

[Completar con cuellos de botella identificados]

## 8. Recomendaciones para Escalabilidad Futura

### Corto Plazo (Próximas 2-4 semanas)
- [Recomendación 1]
- [Recomendación 2]

### Mediano Plazo (1-3 meses)
- Implementar caché con ElastiCache (Redis)
- Optimizar consultas a base de datos
- Implementar CDN con CloudFront

### Largo Plazo (3-6 meses)
- Migrar a arquitectura de microservicios
- Implementar Kubernetes (EKS)
- Implementar disaster recovery multi-región

## 9. Conclusiones

[Completar con conclusiones de las pruebas]

## 10. Anexos

### A. Configuración de JMeter
[Detalles de configuración]

### B. Logs de CloudWatch
[Referencias a logs relevantes]

### C. Gráficas de Monitoreo
[Incluir capturas de CloudWatch]

---

**Documento preparado por**: [Nombres del equipo]
**Fecha de Entrega**: [Fecha]
**Versión Final**: 1.0

## Plan B
### Informe Resumido — Rendimiento del Worker *(videos/min)*  
**Fecha:** 2025-11-09  

---

### Objetivo  
Evaluar el comportamiento del *worker* bajo condiciones de recursos limitados, identificando el punto de saturación del sistema y el impacto en el throughput al incrementar la concurrencia en un entorno de cómputo reducido.

---

### 1. Metodología  

Se replicó el procedimiento empleado en el **Escenario 2**, ejecutando pruebas controladas con **1** y **2** procesos concurrentes.  
La prueba con **4 workers** no pudo completarse debido a las restricciones de la instancia (**2 vCPU / 4 GB RAM**), que provocaban **fallas de estabilidad y reinicio del proceso Celery** al intentar superar ese umbral.  

Cada ejecución mantuvo constantes el dataset, la configuración de Redis y el procedimiento de encolamiento.  
Los *workers* se iniciaron con los siguientes comandos:

```bash
# Concurrencia 1
celery -A app.tasks.celery_app.celery_app worker -Q celery -n w1@%h -c 1 --loglevel=info

# Concurrencia 2
celery -A app.tasks.celery_app.celery_app worker -Q celery -n w1@%h -c 2 --loglevel=info
 ```

La carga de trabajo se generó con el mismo script de 11 tareas consecutivas:
```bash
python3 - <<'PY'
from app.tasks.video_tasks import process_video_task
video_id = "cc9318d6-b922-48c5-b71c-d927d3681a8f"
for _ in range(11):
process_video_task.delay(video_id)
print("✅ Encoladas 11 tareas con éxito")
PY
 ```
## Resultados principales  

**Tabla de rendimiento — Throughput promedio (videos/minuto):**  

<img width="1572" height="979" alt="image" src="https://github.com/user-attachments/assets/1ee338a3-4a65-4925-a1e6-1ca942301711" />


| Concurrencia | 50 MB | 100 MB |
|---------------|-------|--------|
| 1 worker | 1.9 | 0.8 |
| 2 workers | 3.4 | 1.7 |

> ⚠️ *El intento de ejecución con 4 workers provocó un consumo total de CPU (>95 %) y RAM (>3.8 GB), ocasionando el cierre forzado del proceso Celery. No se obtuvieron métricas válidas para este caso.*

---

### Hallazgos clave  

- El sistema mantiene estabilidad hasta **2 workers concurrentes**, pero no dispone de recursos suficientes para escalar más allá.  
- Se observa **caída del throughput (~30 %)** respecto al Escenario 2 debido al incremento de latencia en disco y la contención de CPU.  
- Las tareas de **100 MB** presentan un **tiempo promedio de servicio casi doble**, producto de la decodificación y el acceso a almacenamiento temporal.  
- Durante los picos de carga, la **cola de Redis crece sostenidamente**, aunque sin pérdida de mensajes.  

---

### Métricas observadas  

| Métrica | 50 MB | 100 MB |
|----------|--------|---------|
| Tiempo promedio por tarea | 29 s | 61 s |
| Uso de CPU | hasta 90 % | hasta 95 % |
| RAM | hasta 3.6 GB | hasta 3.9 GB |
| Error rate | 12–20 % (estable) | hasta 50 % bajo saturación |

---

### Recomendaciones  

- Mantener la concurrencia máxima en **2 workers por instancia** de estas características.  
- Evaluar el uso de una **instancia con ≥ 4 vCPU y 8 GB RAM** para escenarios de alta carga.  
- Reducir operaciones de disco implementando **pre-carga en memoria (tmpfs)** o **cacheo local**.  
- Activar **`worker_prefetch_multiplier=1`** y la opción **`-Ofair`** para balancear la distribución de tareas.  
- Incorporar **monitoreo en tiempo real con Prometheus/Grafana** para detectar saturación temprana.  

---

### Conclusión  

El sistema evidencia un **punto de saturación temprano**: con **2 workers** alcanza el máximo rendimiento sostenible (≈ **3.4 videos/min para 50 MB**), mientras que cualquier intento de escalar más allá provoca inestabilidad y caída del servicio.  
A pesar de la reducción intencional de recursos, el *worker* mantiene un comportamiento controlado y confirma la **importancia de dimensionar la infraestructura** según la carga esperada.



