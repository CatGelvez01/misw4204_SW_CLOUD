# MISW – 4204 Desarrollo de Software en la Nube  
**Grupo 15**  

## Análisis de Capacidad

---

### Escenario 1 – Capacidad de la Capa Web (Usuarios Concurrentes)

En este escenario se evaluó la **capacidad de respuesta de la capa Web**, midiendo el comportamiento del sistema ante diferentes volúmenes de usuarios concurrentes.  
Para ello, se **desacopló la capa worker** de la API, evitando procesos de autenticación y preprocesamiento asíncrono con el fin de aislar el rendimiento puro del servicio web.

---

### Modificaciones Implementadas

Se realizaron ajustes en la arquitectura para separar el worker de procesamiento de la API principal, permitiendo que las peticiones HTTP se atiendan directamente sin encolado ni autenticación adicional.
<img width="787" height="647" alt="image" src="https://github.com/user-attachments/assets/fe5fd092-a3a1-4985-8ec3-3fcb8f679a02" />

**Figura 1.** Modificaciones para desacoplar la capa worker  
*(Referencia visual de la arquitectura ajustada para pruebas de carga)*

---

### Diseño de la Prueba

Se desarrolló un **script en Apache JMeter** con el objetivo de evaluar:

- Cantidad de **peticiones por segundo (RPS)**  
- **Porcentaje de error** (% Error)  
- **Tiempo de respuesta medio** (ms)  
- **Rendimiento total** bajo carga progresiva  

El plan de prueba incluye validaciones iniciales de sanidad del sistema antes de aplicar carga masiva, asegurando la correcta disponibilidad del endpoint y la respuesta esperada.
<img width="1176" height="302" alt="image" src="https://github.com/user-attachments/assets/b41b5282-9e3a-4070-9538-fbf73ccc5149" />

**Figura 2.** Creación y configuración del test plan en JMeter  
*(Se valida el estado del sistema y la sanidad del endpoint antes del escalamiento)*

---

### Resultados de la Prueba de Sanidad

- **% de error:** 0 %  
- **Media de respuesta:** 52 ms  
- **Interpretación:** Todas las peticiones fueron exitosas y el sistema respondió de forma inmediata, confirmando que el entorno se encontraba operativo antes de iniciar las pruebas de carga.
<img width="1182" height="173" alt="image" src="https://github.com/user-attachments/assets/925afb8b-78fc-4124-9f4c-4366ae0de505" />

**Figura 3.** Resultados de la prueba de sanidad (sin errores, respuesta estable)

---

## Pruebas de Escalamiento Rápido

El escalamiento rápido se aplicó de manera incremental, aumentando el número de **usuarios concurrentes** durante un período de **3 minutos** para cada iteración.  
Cada ejecución cuenta con su respectiva captura de resultados obtenidos en JMeter.

---

### 1. Escenario con 100 usuarios (3 minutos)

Prueba inicial de carga baja para validar estabilidad del endpoint bajo concurrencia moderada.  
El sistema mantiene tiempos de respuesta constantes y sin errores.  
<img width="1185" height="171" alt="image" src="https://github.com/user-attachments/assets/e5cf3649-7540-4b04-8c55-b35db0aaab95" />

**Figura 4.** Resultado JMeter – 100 usuarios

---

### 2. Escenario con 300 usuarios (3 minutos)

Aumento gradual de carga.  
Se mantiene un desempeño estable, con leve incremento en la media de respuesta pero sin errores reportados.  
<img width="1177" height="177" alt="image" src="https://github.com/user-attachments/assets/29aee487-f5aa-45e5-8a02-378a96172fac" />


**Figura 5.** Resultado JMeter – 300 usuarios

---

### 3. Escenario con 500 usuarios (3 minutos)

Carga media.  
El tiempo de respuesta promedio aumenta ligeramente, aunque todas las peticiones son exitosas.  
<img width="1178" height="203" alt="image" src="https://github.com/user-attachments/assets/0e51d503-a569-4d39-8704-a17a87bf51a9" />

**Figura 6.** Resultado JMeter – 500 usuarios

---

### 4. Escenario con 1000 usuarios (3 minutos)

Escenario de carga alta.  
El sistema mantiene su disponibilidad sin fallas, aunque el tiempo de respuesta se eleva proporcionalmente.  
<img width="1178" height="203" alt="image" src="https://github.com/user-attachments/assets/915d920c-8f08-4ba3-a1cd-adf041353f60" />

**Figura 7.** Resultado JMeter – 1000 usuarios

---

### 5. Escenario con 1500 usuarios (3 minutos)

Se comienza a evidenciar **una ligera degradación del rendimiento**, pero el sistema sigue respondiendo sin errores críticos.  
<img width="1177" height="182" alt="image" src="https://github.com/user-attachments/assets/b24031b7-907f-4fde-bae3-c154e934dd9b" />

**Figura 8.** Resultado JMeter – 1500 usuarios

---

### 6. Escenario con 3000 usuarios (3 minutos)

El sistema alcanza su primer punto de **saturación perceptible**.  
El tiempo medio de respuesta se incrementa notablemente y aparecen algunos retrasos en la cola de peticiones.  
<img width="1180" height="171" alt="image" src="https://github.com/user-attachments/assets/151afe8e-625f-46ee-8ab1-c884f87f6eff" />

**Figura 9.** Resultado JMeter – 3000 usuarios

---

### 7. Escenario con 5000 usuarios (3 minutos)

Carga muy alta.  
Se registran tiempos de respuesta elevados y algunas peticiones comienzan a exceder el umbral de tolerancia configurado en JMeter.  
<img width="1178" height="176" alt="image" src="https://github.com/user-attachments/assets/65a6a132-7167-4435-8f6a-b3f168bfc5a7" />

**Figura 10.** Resultado JMeter – 5000 usuarios

---

### 8. Escenario con 8000 usuarios (3 minutos)

Escenario máximo de carga.  
El sistema muestra **respuestas intermitentes**, con tiempos variables y evidencia de saturación total de recursos de CPU en la capa Web.  
<img width="1183" height="172" alt="image" src="https://github.com/user-attachments/assets/36730045-3de3-471d-958e-53882757ebc5" />

**Figura 11.** Resultado JMeter – 8000 usuarios



---

## Observaciones Generales

- El sistema **mantiene estabilidad** hasta aproximadamente **1500 usuarios concurrentes**.  
- A partir de **3000 usuarios**, el **tiempo medio de respuesta** aumenta de forma considerable.  
- En **5000 usuarios o más**, comienzan a presentarse **timeouts y degradación visible del rendimiento**.  
- No se detectaron **fallos críticos** ni reinicios de contenedores durante las pruebas.  
- El entorno soporta de forma óptima entre **1000–1500 usuarios concurrentes**, siendo necesario **escalar horizontalmente** para cargas superiores.

---

## Conclusiones

El análisis de capacidad demuestra que la **capa Web** de la aplicación ANB Rising Stars Showcase responde adecuadamente bajo cargas moderadas.  
La respuesta se mantiene estable hasta 1500 usuarios concurrentes, con una media de **52–180 ms** dependiendo del nivel de carga.  

**Recomendaciones:**
1. Implementar **balanceo de carga (Nginx, HAProxy o AWS ELB)**.  
2. Desplegar **réplicas adicionales del backend** para manejar más sesiones simultáneas.  
3. Activar **caché HTTP** para endpoints estáticos o de lectura frecuente.  
4. Ajustar **parámetros de concurrencia de Uvicorn/Gunicorn** para mejorar la distribución de carga.  

Con estas optimizaciones, el sistema puede escalar progresivamente y mantener una experiencia de usuario fluida incluso en escenarios de alta concurrencia.


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

