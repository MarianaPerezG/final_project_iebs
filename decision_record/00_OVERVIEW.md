<br>

# Decision Records - Índice General

<br>

Documentación de decisiones técnicas y arquitectura del sistema de recomendación de cursos.

<br>

## Estructura de Documentos

<br>

### Definición de Conceptos Base

- [**definition_global_skills.md**](definition_global_skills.md) — Las 8 habilidades globales y fórmula del gap

<br>

### Módulo 1: Skill Matrix (Empleados)

- [**assignment_skill_scores.md**](assignment_skill_scores.md) — Familias ocupacionales y mapeo de roles
- [**skill_matrix_heuristic.md**](skill_matrix_heuristic.md) — Fórmula base: cálculo per-employee con Education+Performance
- [**adjustment_skill_scores.md**](adjustment_skill_scores.md) — Normalizaciones y pesos por tipo de skill (hard vs soft)

<br>

### Módulo 2: Target Matrix (Objetivos)

- [**skill_demand_vector_aggregation.md**](skill_demand_vector_aggregation.md) — Agregación desde LinkedIn: demanda de mercado
- [**target_matrix_heuristic.md**](target_matrix_heuristic.md) — Fórmula: combinación demand (×0.30) + goals (+0.50)

<br>

###  Módulo 3: Gap & Selección de Cursos

- [**gap_matrix_formula.md**](gap_matrix_formula.md) — Gap = max(target - skill, 0)
- [**course_skills_mapping.md**](course_skills_mapping.md) — Mapeo fuzzy de skills de cursos a global skills

<br>

### Módulo 4: Recomendación

- [**recommendation_model_architecture.md**](recommendation_model_architecture.md) — Modelo hybrid: cached + semantic similarity

<br>

### Transversales

- [**job_title_resolution.md**](job_title_resolution.md) — Mapeo títulos a familias: lexical → semantic
- [**database_schema_design.md**](database_schema_design.md) — SQLite: tablas, índices, queries
- [**evaluation_metrics_strategy.md**](evaluation_metrics_strategy.md) — Métricas: coverage, precision, diversity

<br>

## Flujo de Datos

<br>

```
IBM HR Dataset       LinkedIn Postings       Company Goals        Courses API
      ↓                     ↓                      ↓                   ↓
 Skill Matrix    Skill Demand Vector   Company Goal Skills      Course Skills Matrix
      │           │                     │                              ↓
      │           └─────────────────────┘                              │
      │                      ↓                                         │
      │                Target Matrix                                   │
      │                           ↓                                    │
      └──────────────────────→ Gap Matrix                              │
                                    ↓                                  │
                                    └──────────────────┬───────────────┘
                                                       ↓
                                            Recommendations (top-3)
                                  [Combine: Gap Matrix + Course Skills]
                                                       ↓
                                              Web App + Evaluation
```

**Flujo:**
1. **Matrices base**: Skill Matrix, Target Matrix, Gap Matrix (empleados + brechas)
2. **Courses**: Obtener desde API → Course Skills Matrix  
3. **Recommendation**: Combinar Gap Matrix + Course Skills Matrix → ranking top-3

<br>

## Checklist de Decisiones

<br>

- ✅ Qué 8 skills evaluar → `definition_global_skills.md`
- ✅ Cómo puntuar empleados actuales → `skill_matrix_heuristic.md` + `adjustment_skill_scores.md`
- ✅ Cómo definir objetivos por rol → `assignment_skill_scores.md`
- ✅ Cómo incorporar demanda mercado → `skill_demand_vector_aggregation.md`
- ✅ Cómo combinar: demanda + objetivos → `target_matrix_heuristic.md`
- ✅ Cómo calcular brechas → `gap_matrix_formula.md`
- ✅ Cómo mapear cursos a skills → `course_skills_mapping.md`
- ✅ Cómo recomendar cursos → `recommendation_model_architecture.md`
- ✅ Cómo evaluar recomendaciones → `evaluation_metrics_strategy.md`

<br>
