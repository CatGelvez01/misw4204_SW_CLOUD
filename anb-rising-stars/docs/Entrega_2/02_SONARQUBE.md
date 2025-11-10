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


<img width="1422" height="257" alt="image" src="https://github.com/user-attachments/assets/617741d7-d1d4-4c57-9af8-189a76bba620" />


**Resumen General**
- Métrica	Estado	Valor / Descripción
- Quality Gate	❌ Failed	El proyecto no cumple con uno o más criterios mínimos de calidad
- Security	🔴 E (2 problemas críticos)	Riesgos de seguridad detectados
- Reliability	🟠 C (4 issues)	Existen errores potenciales o bugs menores
- Maintainability	🟢 A (12 code smells)	Buena estructura general, bajo nivel de deuda técnica
- Hotspots Revisados	🔴 0.0%	No se han revisado posibles vulnerabilidades manuales
- Duplicaciones	🟢 0.8%	Nivel bajo, aceptable

**Estado del Quality Gate**
Estado: ❌ Failed

Condiciones evaluadas:
✅ Duplicación < 3% (cumple)
❌ Seguridad con calificación E (falla)
⚠️ Fiabilidad (C) — se recomienda mejora
✅ Mantenibilidad A (cumple)
❌ Hotspots de seguridad no revisados (0%)

**Seguridad**
Hallazgos:

<img width="351" height="242" alt="image" src="https://github.com/user-attachments/assets/63f009f0-f2ee-463b-ac38-12cb3f006b7b" />

2 vulnerabilidades críticas:
- Uso de funciones o dependencias inseguras.
- Posibles riesgos de inyección o manejo inseguro de variables.
- Hotspots: 0% revisados (deben ser evaluados manualmente).

**Fiabilidad (Reliability)**

<img width="341" height="240" alt="image" src="https://github.com/user-attachments/assets/2bd2aa21-86d1-405a-bf5d-7eee3f469dd9" />

Nivel: C (4 issues detectados)

Tipo de problemas:
- Posibles excepciones no manejadas.
- Lógica condicional con riesgo de error.
- Falta de validaciones de datos en algunos endpoints.

**Mantenibilidad**

<img width="339" height="243" alt="image" src="https://github.com/user-attachments/assets/40fc8302-25cc-44e9-8ad3-6e12bd1bb06c" />

Nivel: A
- Code Smells: 12 (de baja severidad)
- Complejidad y duplicación: dentro de límites recomendados.

**Cobertura y Pruebas**
Cobertura automática no reportada.

**Duplicaciones**

<img width="336" height="282" alt="image" src="https://github.com/user-attachments/assets/1a1b65eb-96bc-46e8-81ff-86ed0a08135c" />

- Duplicación total: 0.8%
- Valor aceptable (< 3%)
- Ninguna acción requerida inmediata.

**Cobertura de Pruebas**
Cobertura General:
Actualmente el análisis no reporta cobertura de pruebas unitarias en SonarQube, lo que indica que no se han configurado correctamente los reportes de cobertura o que no existen pruebas automatizadas ejecutadas durante el análisis.

🔴 Cobertura actual: 0%


<img width="338" height="273" alt="image" src="https://github.com/user-attachments/assets/4c95b5e4-7188-4d2f-be2f-c7abc54bc44f" />


**Cobertura por Módulo**
No se dispone de un desglose por módulo debido a la falta de reporte de cobertura.
Una vez configuradas las pruebas, SonarQube podrá mostrar cobertura por cada componente (por ejemplo: controllers, services, models, routes).

**Líneas Cubiertas**
Actualmente, 0 líneas de código están cubiertas por pruebas según el reporte de SonarQube.

Meta recomendada:

Nivel	Porcentaje de Cobertura	Descripción
🟢 Excelente	≥ 80%	Cobertura sólida y sostenible
🟡 Aceptable	60% – 79%	Puede mejorar, riesgo moderado
🔴 Baja	< 60%	Riesgo alto de errores no detectados

**Estado del Quality Gate – SonarQube**
- Aprobado/Rechazado
El estado actual del Quality Gate se encuentra en:

🔴 Rechazado (Failed)

Esto indica que uno o más de los umbrales mínimos definidos por SonarQube no fueron alcanzados.
El sistema marca el proyecto como no conforme hasta que los indicadores clave cumplan los valores definidos en las políticas de calidad.

**Condiciones Evaluadas**
El Quality Gate evalúa automáticamente una serie de métricas de calidad que determinan la aceptabilidad del código antes de ser desplegado.
Las principales condiciones analizadas son:

Métrica	Umbral Mínimo Requerido	Valor Actual	Estado
Cobertura de Pruebas	≥ 80%	0%	🔴 No cumple
Duplicación de Código	≤ 3%	0%	🟢 Cumple
Bugs	0 críticos	2 detectados	🔴 No cumple
Vulnerabilidades	0 críticas	1 detectada	🔴 No cumple
Code Smells	≤ 20	58	🟠 Requiere mejora
Debt Ratio (Deuda Técnica)	≤ 5%	8.7%	🟠 En riesgo

**Tendencias**

El análisis histórico muestra la siguiente evolución:
Fecha	Estado Quality Gate	Cobertura	Bugs	Vulnerabilidades
- 1er Análisis	Rechazado	0%	3	2
- 2do Análisis	Rechazado	15%	2	1
- 3er Análisis (Actual)	Rechazado	0%	2	1



