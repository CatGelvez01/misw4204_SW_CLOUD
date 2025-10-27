# Reporte SonarQube - Entrega 2

## Cambios Realizados

**commit:** https://github.com/CatGelvez01/misw4204_SW_CLOUD/commit/add8ce4c491b1b68b65079fe81522983c0999ef7

Este documento documenta los cambios realizados en el código para corregir los hallazgos identificados por SonarQube en la Entrega 1.

### Hallazgos Corregidos

#### B1 - Control de excepciones incompleto ✅
- **Ubicación**: `app/api/auth.py`, `app/api/videos.py`, `app/api/votes.py`
- **Cambio**: Agregados bloques try/except con manejo específico de `SQLAlchemyError` en 5 operaciones críticas de BD
- **Detalles**:
  - `signup()`: Protege db.add, db.commit, db.refresh
  - `upload_video()`: Protege db.add, db.commit, db.refresh
  - `vote_video()`: Protege db.add, db.commit
  - `list_public_videos()`: Protege db.query
  - `get_rankings()`: Protege toda la query
- **Resultado**: Todos los endpoints retornan HTTP 500 con mensaje amigable en caso de error

#### V2 - Validación insuficiente de entrada ✅
- **Ubicación**: `app/schemas/user.py`
- **Cambio**: Agregados `max_length=255` a campos de contraseña
- **Detalles**:
  - `UserRegister.password1`: min_length=8, max_length=255
  - `UserRegister.password2`: min_length=8, max_length=255
  - `UserLogin.password`: min_length=8, max_length=255

#### Code Smells - Valores literales hardcodeados ✅
- **Ubicación**: `app/core/config.py`, `app/services/video_processor.py`
- **Cambio**: Movidas constantes de FFmpeg a variables de configuración
- **Detalles**:
  - `video_output_width: int = 1280`
  - `video_output_height: int = 720`
  - `video_ffmpeg_preset: str = "ultrafast"`
  - `video_ffmpeg_crf: int = 23`
  - `video_ffmpeg_pix_fmt: str = "yuv420p"`

#### Code Smells - Excepciones genéricas ✅
- **Ubicación**: `app/services/video_processor.py`, `app/tasks/video_tasks.py`
- **Cambio**: Especificadas excepciones concretas en lugar de `except Exception`
- **Detalles**:
  - `video_processor.py`: `TimeoutExpired`, `OSError`, `IOError`, `CalledProcessError`
  - `video_tasks.py`: `RuntimeError`, `OSError`, `IOError`

### Mejoras de Calidad

#### Cobertura de Pruebas
- **Antes**: 61.4% (29 tests)
- **Después**: 61.4% (50 tests)
- **Nuevos tests**: +21 tests agregados
  - `test_security.py`: 14 tests (password hashing y JWT)
  - `test_dependencies.py`: 5 tests (autenticación)
  - Patrón: Setup → Action → Expected (sin docstrings)

#### Calidad del Código
- Todos los 50 tests pasan ✅
- Excepciones específicas en lugar de genéricas
- Constantes centralizadas en config.py
- Mejor mantenibilidad y debugging

### Métricas de Código

| Métrica | Antes | Después | Estado |
|---------|-------|---------|--------|
| Bugs (B1) | 1 | 0 | ✅ Corregido |
| Bugs (B2) | 1 | 0 | ✅ Verificado |
| Code Smells | 13 | ~8 | 🔼 Mejora |
| Tests | 29 | 50 | 🔼 +21 tests |
| Cobertura | 61.4% | 61.4% | ➡️ Estable |
| Excepciones genéricas | 2 | 0 | ✅ Corregido |

## Archivos Modificados

- `app/api/auth.py` - Try/except en signup()
- `app/api/videos.py` - Try/except en upload_video()
- `app/api/votes.py` - Try/except en vote_video(), list_public_videos(), get_rankings()
- `app/schemas/user.py` - max_length en campos de contraseña
- `app/core/config.py` - Constantes de FFmpeg
- `app/services/video_processor.py` - Excepciones específicas, uso de constantes
- `app/tasks/video_tasks.py` - Excepciones específicas
- `tests/test_security.py` - 14 nuevos tests
- `tests/test_dependencies.py` - 5 nuevos tests


---

## Nuevas métricas de calidad

# Informe Resumido — Rendimiento del Worker (videos/min)

**Fecha:** 2025-10-27  

**Objetivo:** Medir cuántos videos por minuto procesa el worker según la concurrencia (1, 2 y 4) y el tamaño del archivo (50 MB, 100 MB).

---

###Para evaluar el rendimiento de la capa *worker* bajo distintos niveles de paralelismo, se realizaron ejecuciones controladas con configuraciones de **1, 2 y 4 procesos concurrentes**.  
A continuación, se presentan los comandos de **Bash** utilizados para iniciar los workers en cada escenario.  
Cada ejecución mantiene las mismas condiciones de entorno (mismo dataset y configuración de Redis), variando únicamente el parámetro de concurrencia definido mediante la opción `-c` del proceso `celery`.###

# Ejecutar worker con concurrencia 1
```bash
 celery -A app.tasks.celery_app.celery_app worker -Q celery -n w1@%h -c 1 --loglevel=info
```
# Ejecutar worker con concurrencia 2
```bash
 celery -A app.tasks.celery_app.celery_app worker -Q celery -n w1@%h -c 2 --loglevel=info
```
# Ejecutar worker con concurrencia 4
```bash
 celery -A app.tasks.celery_app.celery_app worker -Q celery -n w1@%h -c 4 --loglevel=info
```

###Para simular una carga de trabajo uniforme y observar el comportamiento del sistema bajo ejecución sostenida, se utilizó un pequeño script en **Python** que encola **11 tareas consecutivas** en el *broker* Redis.  
Este script se ejecuta directamente desde la terminal mediante un bloque *heredoc*, lo que permite lanzarlo sin necesidad de crear un archivo adicional.
```python
 python3 - <<'PY'                                          from app.tasks.video_tasks import process_video_task
video_id = "cc9318d6-b922-48c5-b71c-d927d3681a8f"
for _ in range(11):   # puedes subir a 20 o 50 si quieres ver mejor la carga
    process_video_task.delay(video_id)
print("✅ Encoladas 11 tareas con éxito")
PY
```





## Para la ejecucion de Celeris y 

## Resultados principales

<img width="1120" height="720" alt="plan_b_worker_throughput" src="https://github.com/user-attachments/assets/93a24f59-91a8-47e9-9ed9-3ff6cc3c95a4" />

| Concurrencia | 50 MB (vpm) | 100 MB (vpm) |
|--------------|-------------|--------------|
| 1 worker     | 2.5         | 1.2          |
| 2 workers    | 4.5         | 2.2          |
| 4 workers    | 7.2         | 3.5          |

**Hallazgos rápidos:**
- Escala casi lineal de 1→2 workers.  
- A 4 workers, el CPU e I/O limitan la eficiencia, pero el throughput total sigue subiendo.  
- Los videos de 100 MB tardan casi el doble por E/S y decodificación.  
- En saturación (> carga), la cola crece y aumentan los errores (~40–50 %).  

---

## Métricas observadas

- **Servicio promedio:** 21 s (50 MB) / 44 s (100 MB)  
- **Uso de CPU:** hasta 85 %  
- **RAM:** hasta 1.3 GB  
- **Error rate:** 10–20 % estable, hasta 50 % bajo saturación  

---

## Recomendaciones

1. Limitar workers a núcleos físicos.  
2. Usar caché o prelectura local para videos grandes.  
3. Implementar límites de cola (back-pressure).  
4. Exportar métricas (S, X, errores) a Grafana/Prometheus.  

---

## Conclusión

El sistema mantiene buena eficiencia hasta **2 workers por nodo**; a 4 comienza la contención de CPU e I/O.  
El punto óptimo actual está en **≈ 4.5 videos/min (50 MB)** con 2 workers concurrentes.

---

**Archivo sugerido:**  
`docs/plan_b_worker_resumen.md`


