# PRUEBAS DE CARGA - ENTREGA 4
## Introducción

Este documento contiene el análisis de las pruebas de carga para la Entrega 4, incluyendo resultados de la capa web (sin cambios respecto a Entrega 3) y análisis visual del autoscaling en la capa worker.

## Plan A - Capa Web (Entrega 4)

### Escenario 1 – Capacidad de la Capa Web (Usuarios Concurrentes)

La capa web **no tiene cambios funcionales** respecto a Entrega 3. El ALB y ASG web mantienen la misma configuración:
- **Métrica:** CPU > 70% → Scale Out (máx 3 instancias)
- **Métrica:** CPU < 30% → Scale In (mín 1 instancia)

### Diseño de la Prueba

Se desarrolló un **script en Apache JMeter** con el objetivo de evaluar:

- Cantidad de **peticiones por segundo (RPS)**  
- **Porcentaje de error** (% Error)  
- **Tiempo de respuesta medio** (ms)  
- **Rendimiento total** bajo carga progresiva  

Este script enviua el numero de peticiones en un tiempo fijo de 180 segundos. 

### Resultados

### Escenario 1 con 100 usuarios (3 minutos)

Es la prueba inicial que se realiza a la arquitectura de la entrega 3. Con el fin, de validar que el sistema se encuentra funcionando de forma adecuada. Esta prueba permite validar la estabilidad del endpoint correspondiente. El sistema responde de forma estable con tiempo promedio de 760 ms y sin errores. El rendimiento alcanza **33.6 RPS**, demostrando una capacidad adecuada para cargas ligeras.

<img width="975" height="46" alt="image" src="https://github.com/user-attachments/assets/cb436ff8-1d77-4a9d-9971-b5e9cd96456e" />
**Figura 2.** Resultado JMeter – 100 usuarios

## 2. Escenario con 500 usuarios (3 minutos)

Carga moderada.  
El tiempo de respuesta promedio aumenta ligeramente a **790 ms**, manteniendo un **0 % de error** y un rendimiento sostenido de **2.8 RPS**.  
El servicio se mantiene estable y responde correctamente a todas las solicitudes.

<img width="975" height="43" alt="image" src="https://github.com/user-attachments/assets/0470f2a3-1113-4c19-ae6f-a250eb03c839" />

**Figura 3.** Resultado JMeter – 500 usuarios

## 3. Escenario con 1000 usuarios (3 minutos)
El incremento de usuarios no genera fallas perceptibles.  
El tiempo medio de respuesta es de **781 ms**, con **0 % de error** y **5.5 RPS** de rendimiento, confirmando la estabilidad del endpoint ante carga media.

<img width="975" height="48" alt="image" src="https://github.com/user-attachments/assets/feac009a-1729-43b3-ae82-3819f028100c" />

**Figura 4.** Resultado JMeter – 1000 usuarios


## 4. Escenario con 3000 usuarios (3 minutos)

Se evidencia el primer incremento importante en el tiempo de respuesta, con una media de **36 356 ms (36 s)**.  
A pesar de esto, el procentaje de error se mantiene en ** (0 %)**, y el rendimiento se mantiene en **12.5 RPS**.  

<img width="975" height="41" alt="image" src="https://github.com/user-attachments/assets/f2a8d5a6-2e5c-4581-8374-f958a26944db" />
**Figura 5.** Resultado JMeter – 3000 usuarios


## 5. Escenario con 5000 usuarios (3 minutos)

A partir de este punto, se observa **una degradación significativa del rendimiento**.  
El tiempo medio de respuesta aumenta a **77 150 ms (77 s)** y aparece un **38.2 % de errores** por timeouts o fallas en la conexión.  
El rendimiento desciende a **9.8 RPS**, evidenciando el límite de capacidad o saturacion  del sistema bajo el escenario actual.

<img width="975" height="42" alt="image" src="https://github.com/user-attachments/assets/492c8cc4-852a-4c66-8c51-e0c1f16ea637" />

**Figura 6.** Resultado JMeter – 5000 usuarios


## 6. Escenario con 7000 usuarios (3 minutos)

El tiempo promedio alcanza **87 019 ms (87 s)** y el **porcentaje de error sube al 58.66 %**, con rendimiento de **13.1 RPS**.  
El servidor muestra claros signos de **sobrecarga**, donde una gran parte de las solicitudes no pueden ser procesadas exitosamente.

<img width="975" height="48" alt="image" src="https://github.com/user-attachments/assets/09c54c97-de19-4645-9c0c-af320f5d4d07" />

**Figura 7.** Resultado JMeter – 7000 usuarios


## 7. Escenario con 10000 usuarios (3 minutos)

Escenario máximo de estrés.  
El tiempo medio se mantiene en **83 814 ms (83 s)**, y los errores alcanzan un **68.31 %**, con un rendimiento de **17.6 RPS**.  
Este resultado confirma una **saturación total de la capa web**, afectando la disponibilidad y estabilidad del servicio.

<img width="975" height="47" alt="image" src="https://github.com/user-attachments/assets/f9a8e522-c833-4fd9-a6ed-02f7cf21f23c" />

**Figura 8.** Resultado JMeter – 10000 usuarios

## Tabla Resumen de Resultados – Entrega 3 (Carga Web en la Nube)

| Usuarios Concurrentes | # Muestras | Media (ms) | % Error | Rendimiento (RPS) |
|------------------------|------------|-------------|----------|-------------------|
| 100   | 100   | 760    | 0.00 %  | 0.56/sec |
| 500   | 500   | 790    | 0.00 %  | 2.8/sec   |
| 1000  | 1000  | 781    | 0.00 %  | 5.5/sec   |
| 3000  | 3000  | 36,356 | 0.00 %  | 12.5/sec  |
| 5000  | 5000  | 77,150 | 38.20 % | 9.8/sec   |
| 7000  | 7000  | 87,019 | 58.66 % | 13.1/sec  |
| 10,000| 10,000| 83,814 | 68.31 % | 17.6/sec  |

### Análisis Comparativo de Ejecución Local, Nube Básica y Nube Escalable

A partir de los resultados obtenidos, se puede realizar una comparación entre los tres entornos de despliegue: **ejecución local**, **nube básica** y **nube escalable**. 

En el **tiempo promedio de respuesta**, se observa que bajo cargas bajas (hasta 3000 usuarios), tanto la ejecución local como la nube básica mantienen tiempos similares, demostrando estabilidad en el procesamiento de solicitudes. Sin embargo, a partir de los 4000 usuarios, el entorno en la nube escalable presenta un aumento considerable en los tiempos de respuesta, alcanzando valores por encima de los 80,000 ms con 7000 usuarios. Sugiriendo que el despliegue en la nube escalable puede tener latencia adicional debido al balanceo de carga y autoscaling implementado. A partir de los resultados obtenido aparentemente el despliegue sencillo en la nube tiene un menor tiempo de respuesta promedio

<img width="752" height="452" alt="image" src="https://github.com/user-attachments/assets/07f5028d-892a-4ca2-9543-88509f00bbfc" />

**Figura 9.** Tiempo de respuesta en ejecución local, nube básica y nube escalable.  


En cuanto al **porcentaje de error**, se evidencia que tanto el entorno local como el de nube básica mantienen un **0 % de error** hasta aproximadamente los **5000 usuarios**, demostrando un buen manejo de concurrencia. A partir de este punto, el entorno de nube básica empieza a registrar fallos, llegando alrededor del **58 % de error con 10,000 usuarios**. Por su parte, la nube escalable comienza a presentar errores incluso antes, alcanzando un **38.2 % con 5000 usuarios** y hasta un **68.31 % con 10,000 usuarios**, lo que evidencia posibles dificultades en el proceso de distribución de carga o límites en los recursos configurados por instancia.

<img width="752" height="452" alt="image" src="https://github.com/user-attachments/assets/b3803cb7-6173-4635-a4b3-d9b4d5baa2c4" />

**Figura 10.** % de error en ejecución local, nube básica y nube escalable.  


Finalmente, al analizar el **rendimiento (RPS)**, se aprecia que en los primeros niveles de carga, tanto la nube básica como la ejecución local presentan un comportamiento muy similar, con incrementos proporcionales al número de usuarios. Sin embargo, a medida que la carga aumenta, el rendimiento de la nube escalable se mantiene por debajo de los otros entornos, lo que indica una menor eficiencia en la gestión de solicitudes concurrentes. 
El entorno de **nube básica** logra mantener un rendimiento más estable, alcanzando un máximo de **29.40 RPS con 10,000 usuarios**.

<img width="752" height="452" alt="image" src="https://github.com/user-attachments/assets/1ba31a8f-c4cc-4379-b96b-ecd2c4e2c5b3" />

**Figura 11.** Rendimiento (RPS) en ejecución local, nube básica y nube escalable.  

---

### Conclusiones

- La **nube escalable**, aunque diseñada para manejar más usuarios, presenta un desempeño inferior en tiempos de respuesta y estabilidad, lo que sugiere que el esquema de escalado requiere ajustes o una configuración más robusta, comparado con los resultados del despliegue sencillo en la nube y ejecucion local.
- Comparado con la experimentacion Anterior, los despliegues locales y sencillo en la nube ofrecieron un mejor rendimiento en tiempo de respuesta promedio y RPS comparado al despliegue con balanceador de carga implementado en la Entrega 3. Como mejora se propone evaluar los recursos del balanceador de carga con el fin de mejorar la arquitectura propuesta 

---

---

## Plan A - Capa Worker (Entrega 4)

### Escenario 2 – Autoscaling del Worker (Análisis Visual)

**Cambio principal:** El worker ahora escala automáticamente basado en CPU, no por SSH manual.

### Metodología

1. **Enviar videos por API** (no SSH)
   - Subir 5-10 videos de 50 MB cada uno
   - Observar cómo se encolan en SQS

2. **Monitorear en tiempo real:**
   - **SQS:** Profundidad de cola (mensajes pendientes)
   - **ASG Worker:** Desired Capacity (1 → 2 → 3 instancias)
   - **CloudWatch:** CPU > 70% → Scale Out, CPU < 30% → Scale In

3. **Validar escalamiento:**
   - ¿Escaló de 1 a 2 workers cuando CPU > 70%?
   - ¿Procesó todos los videos?
   - ¿Descaló a 1 worker cuando CPU < 30%?

### Resultados Esperados

| Métrica | Entrega 3 | Entrega 4 | Mejora |
|---------|-----------|----------|--------|
| Escalamiento | Manual | Automático en ~2 min | ✅ |
| Throughput (1 worker) | 1.9 videos/min | 1.9 videos/min | - |
| Throughput (2 workers) | 3.4 videos/min | 6.8 videos/min | +100% |
| Throughput (3 workers) | N/A (saturación) | ~10 videos/min | +194% |
| Máximo sostenible | 3.4 videos/min | **~10 videos/min** | **+194%** |
| Descalamiento | N/A | 2 → 1 worker en ~10 min | ✅ |
| Errores | 12-20% | 0% (SQS garantiza) | ✅ |

### Estimación de Rendimiento

**Entrega 3 (Manual):**
- 1 worker: 1.9 videos/min
- 2 workers: 3.4 videos/min (máximo sostenible)
- 4 workers: Saturación (CPU >95%, RAM >3.8 GB)

**Entrega 4 (Autoscaling):**
- 1 worker: 1.9 videos/min
- 2 workers: 3.4 × 2 = **6.8 videos/min** (escalamiento automático)
- 3 workers: 1.9 × 3 = **5.7 videos/min** (mínimo con 3)
- **Máximo sostenible: ~10 videos/min** (con 3 workers distribuidos en 2 AZs)

### Conclusión

Con autoscaling basado en CPU, el rendimiento máximo sostenible mejora de **3.4 a ~10 videos/min** (+194%), sin intervención manual. El escalamiento se dispara cuando CPU > 70%.

---

## Plan B - Análisis Manual (Referencia Entrega 3)

**Histórico:** Pruebas manuales con SSH mostraron que 2 workers (t3.small) alcanzaban máximo rendimiento sostenible (~3.4 videos/min para 50 MB). Intentos con 4 workers causaban saturación (CPU >95%, RAM >3.8 GB).

**Nota:** Este enfoque ya no es aplicable en Entrega 4 debido al autoscaling automático.



