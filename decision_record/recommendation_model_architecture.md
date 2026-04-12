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


## Lógica de Decisión (Híbrida)

```
recommend_for_user(user_id, model_path, csv_path, topk)
    |
    ├─ if csv_path and csv_existe:
    |    └─ buscar user_id en CSV
    |         ├─ ENCONTRADO → retornar cached 
    |         └─ NO ENCONTRADO → continuar
    |
    └─ cargar model desde modelo.pkl
       calcular cosine_similarity(gap_user vs todos_cursos)
       rank top-k
       retornar 
```

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
