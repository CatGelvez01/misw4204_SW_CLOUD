# Plan B – Análisis de Capacidad

Este documento presenta el **Plan B** del proyecto **ANB Rising Stars Showcase**, enfocado en evaluar la capacidad y rendimiento de la aplicación desplegada en un entorno **dockerizado local**.  
El objetivo es medir el comportamiento del sistema bajo diferentes niveles de carga, analizando el uso de **CPU**, **memoria** y **estabilidad** durante el procesamiento intensivo de videos.

Las pruebas se realizaron sobre los principales servicios —**Backend**, **Celery Worker**, **Redis**, **PostgreSQL** y **Nginx**—, destacando el análisis del **worker de video**, encargado de ejecutar tareas **FFmpeg** en paralelo.  
A través de ejecuciones masivas y monitoreo en tiempo real, se identificaron patrones de consumo, posibles cuellos de botella y la resiliencia general del sistema frente a escenarios de alta demanda.

A continuación, se presentan los registros visuales obtenidos durante la ejecución de las pruebas de capacidad.  
Cada captura de pantalla evidencia el estado del sistema, los comandos utilizados y las respuestas generadas en consola, validando así el correcto funcionamiento de todos los componentes involucrados.

---

## Estado Inicial
<img width="1422" height="397" alt="image" src="https://github.com/user-attachments/assets/3fdc463a-d720-4fde-8ec5-6b5a2bfe197d" />

Antes de iniciar las pruebas, se verificó que todos los servicios del entorno dockerizado estuvieran activos y en estado **Healthy**.  
La siguiente imagen muestra la salida del comando `docker compose ps`, donde se confirman los contenedores **backend**, **celery_worker**, **redis**, **postgres** y **nginx** funcionando correctamente.

---

## Verificación del endpoint principal
<img width="1415" height="327" alt="image" src="https://github.com/user-attachments/assets/8e21ca0f-9f48-44e5-94d9-25e9ed79044e" />

Se comprobó el correcto despliegue del backend y la respuesta del servicio **FastAPI** mediante una solicitud **curl** al endpoint raíz (`http://localhost:8080/`).  
La salida devuelve un código **HTTP 200 OK** y un mensaje **JSON** indicando que la API se encuentra en ejecución.

---

## Subida autenticada de un video
<img width="1413" height="210" alt="image" src="https://github.com/user-attachments/assets/5674c300-eee0-43b4-8ba4-f9d3fe22e75a" />

La siguiente captura muestra la ejecución del endpoint `/api/videos/upload`, enviando un archivo de video (`anb_intro.mp4`) junto con un token **JWT** válido.  
La respuesta confirma que el video fue recibido y que el **procesamiento asíncrono** ha sido encolado en **Celery** correctamente.

---

## Ejecución de ráfaga de tareas (Burst de 50)
<img width="1417" height="173" alt="image" src="https://github.com/user-attachments/assets/fa4a4506-c5f1-4b3e-9ee1-e5445511f68e" />

En esta prueba se utilizó el script `bench_producer.py` para encolar **50 tareas consecutivas** de procesamiento de video, simulando una carga alta sobre el sistema.  
La consola muestra los mensajes `[producer]` que confirman la correcta generación y envío de las tareas hacia **Redis**.

---

## Logs de procesamiento concurrente (Celery Worker)
<img width="1182" height="681" alt="image" src="https://github.com/user-attachments/assets/bec51be2-3211-4ac3-bb7b-958f153564d7" />

El siguiente registro corresponde a los logs en tiempo real del contenedor **celery_worker**, obtenidos con `docker compose logs -f celery_worker`.  
Se observa el procesamiento simultáneo de múltiples tareas, la ejecución de **FFmpeg** y los mensajes de éxito (`Video processed successfully`) que validan el flujo completo de trabajo.

---

## Monitoreo de Recursos

En la siguiente figura se muestran tres capturas consecutivas del comando `docker stats`, tomadas en diferentes momentos del procesamiento masivo de videos.  
Cada bloque refleja el comportamiento progresivo del sistema a medida que las tareas Celery se ejecutan y completan.

---

### Primera captura — Inicio del procesamiento
<img width="1178" height="168" alt="image" src="https://github.com/user-attachments/assets/47e20c97-cf15-4dc0-8a46-50042e373dc2" />

La primera captura de `docker stats` corresponde a un momento de reposo, sin tareas activas en la cola de procesamiento.  
En esta etapa, los contenedores del entorno se encuentran inicializados pero sin carga significativa, mostrando niveles mínimos de uso de CPU y memoria.

---

### Segunda captura — Inicio del procesamiento
<img width="1178" height="167" alt="image" src="https://github.com/user-attachments/assets/ee6a6bea-b41c-4e4a-b8b2-8bba9649aa8d" />

En la segunda sección se observa el inicio de la ráfaga de tareas.  
El contenedor **anb_celery_worker** ya presenta una actividad elevada de CPU (≈1200 %) debido al uso de varios procesos FFmpeg en paralelo, aunque el consumo de memoria aún se mantiene estable (~1.7 GB).  
Los demás servicios (**backend**, **nginx**, **postgres**, **redis**) registran una utilización mínima, evidenciando que la carga principal recae sobre el worker de procesamiento.

---

### Tercera captura — Pico máximo de carga
<img width="1181" height="168" alt="image" src="https://github.com/user-attachments/assets/f8c1e778-5e6b-4ad6-93ac-696cd10f4dab" />

En el tercer bloque, el sistema alcanza su punto de máxima demanda de recursos.  
El **celery_worker** sostiene un consumo intensivo de CPU (≈1200 %) y memoria cercana a 1.7 GB, procesando múltiples videos simultáneamente.  
El resto de los contenedores mantienen niveles bajos y estables: **backend** y **nginx** usan menos de 100 MB, mientras que **postgres** y **redis** se mantienen por debajo del 1 % de CPU, confirmando que no existen cuellos de botella en la comunicación ni en las bases de datos.

---

### Cuarta captura — Fase de estabilización
<img width="1177" height="172" alt="image" src="https://github.com/user-attachments/assets/c769c463-13c8-4a0c-be73-559e6f817204" />

En la cuarta medición se aprecia la disminución gradual de la carga una vez que la mayoría de las tareas finalizan.  
Aunque el worker sigue mostrando valores altos de CPU por procesos residuales de FFmpeg, la tendencia es decreciente y los contenedores restantes permanecen estables.  
El sistema logra liberar recursos sin reinicios ni bloqueos, confirmando una buena gestión de memoria y estabilidad post-procesamiento.

---

## Resultados de procesamiento en la carpeta compartida
<img width="860" height="395" alt="image" src="https://github.com/user-attachments/assets/3f8007c5-cc55-4173-87e0-11371aa8f3da" />

Finalmente, se verificó la generación de los archivos de salida en la carpeta `processed/`, donde se almacenan los videos concatenados y renderizados por FFmpeg.  
La captura corresponde al listado obtenido con `ls -lh processed/`, confirmando la creación de los resultados finales.

---

## Conclusiones y análisis del Plan B

A continuación, se presentan las respuestas a los aspectos evaluados en el plan de capacidad del sistema:

### Capacidad nominal (videos/min)

Durante las pruebas con archivos de ~50 MB y un worker Celery con concurrencia de 2 procesos, se alcanzó un rendimiento promedio de **3 a 4 videos procesados por minuto**.  
El sistema mantuvo tiempos de procesamiento estables entre **17 y 20 segundos por video**, sin interrupciones ni fallos.  
Esto permite estimar una capacidad nominal de **180–240 videos por hora** en la configuración actual.

---

### Estabilidad del sistema

A lo largo de las ejecuciones masivas (bursts de 50 y 100 tareas), la **cola Redis** no presentó saturación, y todas las tareas fueron procesadas exitosamente.  
No se observó crecimiento incontrolado en el tamaño de la cola ni errores de concurrencia.  
El worker mostró comportamiento estable y resiliente, con reintentos automáticos controlados y recuperación exitosa de tareas fallidas.

---

### Puntos de saturación y cuellos de botella

Los indicadores de `docker stats` muestran que el uso de **CPU** del worker alcanzó picos de entre **1100 % y 1280 %**, lo que evidencia que la CPU fue el principal cuello de botella durante la ejecución intensiva.  
La memoria, en cambio, se mantuvo estable (~1.7 GB / 15 GB totales), y no se identificaron limitaciones en I/O o en la red.  
El sistema podría escalar **verticalmente** (más núcleos de CPU) o mediante **múltiples workers distribuidos**.

---

### Comportamiento de los recursos

El monitoreo por `docker stats` reflejó:

- **CPU:** saturación temporal en el worker, coherente con la naturaleza intensiva de FFmpeg.  
- **Memoria:** uso constante entre 11–12 %, sin fugas ni crecimiento sostenido.  
- **I/O:** actividad moderada en disco, principalmente al escribir videos procesados.  
- **Redis y PostgreSQL:** consumo mínimo (<2 % CPU, <0.1 GB RAM), sin evidencias de cuello de botella.

---

## Conclusión general

El sistema demuestra **buena capacidad y estabilidad** para procesamiento concurrente de tareas multimedia.  
La arquitectura basada en **FastAPI + Celery + Redis + PostgreSQL** responde adecuadamente bajo escenarios de alta demanda, manteniendo el aislamiento entre servicios y la recuperación automática de tareas fallidas.  
Para cargas mayores (**100+ tareas simultáneas** o archivos **>100 MB**), se recomienda **aumentar la concurrencia** de Celery a 4 o **añadir un segundo nodo worker**, optimizando así el **throughput total del sistema**.
