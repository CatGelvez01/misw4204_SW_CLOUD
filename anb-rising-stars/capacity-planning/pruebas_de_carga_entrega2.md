# Análisis de Pruebas de Carga - Entrega 2

## Introducción

Este documento contiene el análisis detallado de las pruebas de carga ejecutadas en la Entrega 2, incluyendo los resultados de los escenarios planteados y recomendaciones para escalar la solución.

### Escenario 1 – Capacidad de la Capa Web (Usuarios Concurrentes)

En este escenario se evaluó la **capacidad de respuesta de la capa Web**, midiendo el comportamiento del sistema ante diferentes volúmenes de usuarios concurrentes.  
Para ello, se **desacopló la capa worker** de la API, evitando procesos de autenticación y preprocesamiento asíncrono con el fin de aislar el rendimiento puro del servicio web. Las modificaciones realizadas a los endpoints se pueden visualizar en la rama web-layer-capacity. 

---

### Modificaciones Implementadas

Se realizaron ajustes en la arquitectura para separar el worker de procesamiento de la API principal, permitiendo que las peticiones HTTP se atiendan directamente sin encolado ni autenticación adicional.
<img width="787" height="647" alt="image" src="https://github.com/user-attachments/assets/fe5fd092-a3a1-4985-8ec3-3fcb8f679a02" />

**Figura 1.** Modificaciones para desacoplar la capa worker disponible en la rama web-layer-capacity
*(Referencia visual de la arquitectura ajustada para pruebas de carga)*

---

### Descripcion - Diseño de la Prueba

Se desarrolló un **script en Apache JMeter** con el objetivo de evaluar:

- Cantidad de **peticiones por segundo (RPS)**  
- **Porcentaje de error** (% Error)  
- **Tiempo de respuesta medio** (ms)  
- **Rendimiento total** bajo carga progresiva  

### Resultados


### Escenario 1 con 100 usuarios (3 minutos)

Prueba inicial de carga baja para validar la estabilidad del endpoint bajo concurrencia moderada.  
El sistema mantiene tiempos de respuesta constantes y sin errores.  

<img width="975" height="61" alt="image" src="https://github.com/user-attachments/assets/e22cef24-9982-431e-be97-14c53c0eac42" />

**Figura 2.** Resultado JMeter – 100 usuarios 

---

### Escenario 2 con 500 usuarios (3 minutos)

Carga media inicial.  
El sistema conserva un comportamiento estable con un leve incremento en el tiempo promedio de respuesta.  
No se registraron errores.  

<img width="975" height="58" alt="image" src="https://github.com/user-attachments/assets/01b247d7-8141-4518-8c19-a3cdade7efbb" />

**Figura 3.** Resultado JMeter – 500 usuarios  

---

### Escenario 3 con 1000 usuarios (3 minutos)

Aumento de carga significativa.  
El sistema mantiene su disponibilidad sin fallas, aunque el tiempo medio se eleva proporcionalmente al número de usuarios concurrentes.  

<img width="975" height="66" alt="image" src="https://github.com/user-attachments/assets/1144592a-f735-4971-b804-0650f523484c" />

**Figura 4.** Resultado JMeter – 1000 usuarios  

---

### Escenario 4 con 3000 usuarios (3 minutos)

El sistema alcanza su primer punto de **saturación perceptible**.  
A pesar de mantener todas las solicitudes exitosas, el tiempo de respuesta crece y se evidencian retrasos en la cola de peticiones.  

<img width="975" height="58" alt="image" src="https://github.com/user-attachments/assets/6d09e2d0-3714-471a-9e68-e2444293b291" />

**Figura 5.** Resultado JMeter – 3000 usuarios  

---

### Escenario 5 con 5000 usuarios (3 minutos)

Carga muy alta.  
Se observan tiempos de respuesta significativamente mayores, aunque sin errores registrados.  
Comienza a evidenciarse una sobrecarga de recursos en la capa web.  

<img width="975" height="65" alt="image" src="https://github.com/user-attachments/assets/ceee2583-4865-456e-b9e6-8e07a2bf4cdf" />

**Figura 6.** Resultado JMeter – 5000 usuarios  

---

### Escenario 6 con 7000 usuarios (3 minutos)

El sistema empieza a mostrar **inestabilidad y degradación notable**.  
Se incrementa la desviación estándar y aparecen errores en las respuestas debido a timeouts.  

<img width="975" height="62" alt="image" src="https://github.com/user-attachments/assets/7d1811da-4412-4085-8c53-50685c8f9226" />

**Figura 7.** Resultado JMeter – 7000 usuarios  

---

### Escenario 7 con 10,000 usuarios (3 minutos)

Escenario máximo de carga.  
El sistema presenta **saturación total** de recursos, con tiempos de respuesta extremadamente altos y más de la mitad de las peticiones con error.  
Se alcanza el límite de capacidad de la capa Web.  

<img width="975" height="60" alt="image" src="https://github.com/user-attachments/assets/8c0987e0-e9b2-4374-9cff-258efa0d0961" />

**Figura 8.** Resultado JMeter – 10,000 usuarios  

--- 

## Tabla Resumen de Resultados

La siguiente tabla resume el resultados de los diferentes escenarios que evaluaron el desempeño del servicio **Upload Video** bajo distintos volúmenes de usuarios concurrentes.  
A continuación, se presentan los resultados obtenidos:

| Usuarios Concurrentes | # Muestras | Media (ms) | % Error | Rendimiento | 
|------------------------|------------|-------------|-----------|-----------|
| 100   | 100  | 762   |  0.00 % | 33.5/min  |
| 500   | 500  | 743   |  0.00 % | 2.8/sec |
| 1000  | 1000 | 754   | 0.00 % | 5.5/sec | 
| 3000  | 3000 | 857   |  0.00 % | 16.5/sec | 
| 5000  | 5000 | 16,702 |  0.00 % | 24.1/sec | 
| 7000  | 7000 | 50,339 | 35.09 % | 19.7/sec | 
| 10,000| 10,000| 46,649 |  54.76 % | 29.4/sec | 

---



### Análisis

(Por completar)

## Escenario 2

### Descripción
(Por completar)

### Resultados
(Por completar)

### Análisis
(Por completar)

## Conclusiones

(Por completar)

## Recomendaciones para Escalabilidad

(Por completar)

## Consideraciones Adicionales

(Por completar)
