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


`docs/plan_b_worker_resumen.md`


