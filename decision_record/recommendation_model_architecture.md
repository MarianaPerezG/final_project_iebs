# Sistema de Recomendación de Cursos por Usuario (Arquitectura Hybrid)

## Arquitectura: Batch + On-Demand

La arquitectura implementada es **Hybrid**:
- **Batch (CSV)**: Pre-calcula recomendaciones para usuarios existentes → CSV rápido
- **On-Demand (Modelo)**: Usuarios nuevos se calculan en vivo sin reentrenamiento

## Cambios Arquitectónicos

Se ha refactorizado el sistema de recomendación de cursos para separar:
1. **Entrenamiento/Carga del modelo** (`CourseRecommendationModel`) — carga y valida datos
2. **Recomendación** (`CourseRecommender`) — genera recomendaciones usando el modelo
3. **Consultas por usuario (Hybrid)** (`recommend_for_user()`) — inteligente: caché + on-demand

## Flujo de Uso

### 1. Entrenamiento e Indexación Batch (Una sola vez)

```bash
python src/main.py
```

Esto:
- Carga `gap_matrix_result.csv` y `course_skills_matrix.csv`
- Valida que tengan las columnas necesarias
- Entrena el modelo (carga datos en memoria)
- **Guarda el modelo en `models/trained/course_recommendation_model.pkl`**
- **Genera recomendaciones batch para todos los usuarios** → `data/final/course_recommendations.csv`

### 2. Consulta por Usuario - Modo Híbrido

#### Desde CLI:

```bash
# Para usuario existente (CACHÉ - muy rápido, <10ms):
python recommend_user.py --user-id 1
# → Busca en CSV, devuelve en 10ms

# Para usuario nuevo (ON-DEMAND - más lento, ~500ms):
python recommend_user.py --user-id 9999
# → Carga modelo, calcula cosine_similarity, devuelve en ~500ms

# Forzar recálculo on-demand:
python recommend_user.py --user-id 1 --skip-cache

# Diferentes formatos:
python recommend_user.py --user-id 5 --format json
python recommend_user.py --user-id 10 --format csv
```

#### Desde Python:

```python
from src.recommender.recommend_courses import recommend_for_user

# Uso básico (automáticamente usa caché si existe)
recs = recommend_for_user(
    user_id=1,
    model_path="models/trained/course_recommendation_model.pkl",
    csv_path="data/final/course_recommendations.csv",  # Si existe, usa caché
    topk=3
)

# Usuario nuevo (csv_path=None fuerza on-demand)
recs_new = recommend_for_user(
    user_id=9999,
    model_path="models/trained/course_recommendation_model.pkl",
    csv_path=None,  # On-demand siempre
    topk=3
)

for rec in recs:
    print(f"Curso: {rec['course_title']}")
    print(f"Score: {rec['final_score']:.3f}")
```

## Lógica de Decisión (Híbrida)

```
recommend_for_user(user_id, model_path, csv_path, topk)
    |
    ├─ if csv_path and csv_existe:
    |    └─ buscar user_id en CSV
    |         ├─ ENCONTRADO → retornar cached (RÁPIDO ~10ms)
    |         └─ NO ENCONTRADO → continuar
    |
    └─ cargar model desde modelo.pkl
       calcular cosine_similarity(gap_user vs todos_cursos)
       rank top-k
       retornar (LENTO ~500ms pero funciona para nuevos)
```

## Comparativa de Rendimiento

| Escenario | Tiempo | Fuente | Pasos |
|-----------|--------|--------|-------|
| Usuario en CSV | ~10ms | CSV (caché) | 1: lookup |
| Usuario nuevo | ~500ms | Modelo (on-demand) | 3: cargar + cálculo + rank |
| Forzar recalc | ~500ms | Modelo | 3: cargar + cálculo + rank |

## Arquitectura del Modelo

### CourseRecommendationModel
- **Responsabilidad**: Cargar, validar y cachear datos
- **Métodos**:
  - `__init__(gap_matrix_path, course_matrix_path, global_skills)` — inicializar
  - `save()` — guardar estado en pickle
  - `load(model_path)` — cargar modelo guardado (class method)

### CourseRecommender
- **Responsabilidad**: Generar recomendaciones usando un modelo
- **Métodos**:
  - `recommend(employee_id, topk)` — top-k para un usuario
  - `recommend_all(topk)` — top-k para todos los usuarios (retorna DataFrame)

### Funciones Públicas
- `train_and_save_model(config)` — Entrena y guarda modelo
- `recommend_courses(config)` — Pipeline completo (entrena + genera batch)
- `recommend_for_user(user_id, model_path, csv_path, topk)` — **Consulta inteligente (hybrid)**
- `_get_cached_recommendations(user_id, csv_path, topk)` — Helper para búsqueda en CSV

## Ventajas de la Arquitectura Hybrid

✅ **Rendimiento dual**:
  - Usuarios existentes: muy rápido (caché)
  - Usuarios nuevos: flexible (on-demand)

✅ **Escalabilidad**: 
  - No need reentrenamiento para nuevos usuarios
  - No precalcula innecesariamente

✅ **Robustez**: 
  - Si falla CSV, sigue funcionando con modelo
  - Fallback automático

✅ **Claridad**: 
  - Lógica transparente en `recommend_for_user()`
  - Decisión automática caché/on-demand

✅ **Flexibilidad**: 
  - Permite skip-cache si quieres siempre on-demand
  - Paths configurables

## Ubicaciones Clave

- **Modelo entrenado**: `models/trained/course_recommendation_model.pkl`
- **Recomendaciones batch (caché)**: `data/final/course_recommendations.csv`
- **Script CLI**: `recommend_user.py` (raíz del proyecto)
- **Código backend**: `src/recommender/recommend_courses.py`
- **Tests/Ejemplos**: `recommend_user.py --user-id <id>`

## Ejemplo Completo

```bash
# 1. Entrenar modelo y generar batch (primera vez)
python src/main.py
# → Genera: modelo.pkl + course_recommendations.csv

# 2. Usuário existente (desde caché):
python recommend_user.py --user-id 100
# ✓ Rápido: lookups en CSV

# 3. Usuario nuevo (recalcula on-demand):
python recommend_user.py --user-id 9999
# ✓ Flexible: usa modelo sin reentrenamiento

# 4. Forzar recalc incluso para existentes:
python recommend_user.py --user-id 100 --skip-cache

# 5. Integración en Python:
python -c "
from src.recommender.recommend_courses import recommend_for_user
recs = recommend_for_user(100, 'models/trained/course_recommendation_model.pkl', 'data/final/course_recommendations.csv')
for r in recs:
    print(r['course_title'], r['final_score'])
"
```

## Evolución Futura

- Índice vectorial FAISS: si mucha load en on-demand (100+ consultas/seg)
- Updates incrementales: agregar usuarios/cursos sin reentrenamiento completo
- API REST: exponer `recommend_for_user()` como endpoint
- Caché en DB: persistencia de consultas frecuentes
- A/B testing: comparar batch vs on-demand en producción

---

**Decisión grabada:** 2026-04-06  
**Equipo:** Data Science  
**Estado:** Implementado (Hybrid)  
**Tipo:** Batch + On-Demand
