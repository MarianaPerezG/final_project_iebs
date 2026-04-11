<br>

# Evaluation Metrics Strategy

<br>

La estrategia de evaluación mide la calidad de las recomendaciones aplicando métricas de información retrieval y cobertura. Se genera un reporte en `data/reports/recommendation_evaluation.txt`.

<br>

## Métricas Principales

<br>

### 1. Coverage (Cobertura)

$$
\text{coverage} = \frac{\text{# empleados con ≥1 recomendación}}{\text{# total empleados}}
$$

**Interpretación**: % de empleados que reciben sugerencias  
**Objetivo**: > 90%  
**Si baja**: Revisar mapping de skills de cursos

<br>

### 2. Precision@K

$$
\text{precision}@k = \frac{\text{# cursos relevantes en top-k}}{\text{k}}
$$

Donde "relevante" = curso cubre ≥1 skill con gap > 1.0

**Típico**: Precision@3 ≈ 0.80 (2-3 cursos relevantes de los 3 recomendados)

<br>

### 3. Diversity (Diversidad)

$$
\text{diversity} = 1 - \frac{\sum_{e} (\text{subject variance})}{n_{\text{employees}}}
$$

Evita recomendar siempre los mismos cursos. Mide si dataset de cursos tiene variedad de temas.

**Objetivo**: > 0.70 (70% de recomendaciones cubren topics distintos)

<br>

### 4. Gap Coverage Ratio

$$
\text{gap\_coverage}(e) = \frac{\sum_{\text{skills cubiertos}} \text{gap}(e, s)}{\sum_{\text{todos skills}} \text{gap}(e, s)}
$$

Suma de gaps que el set de cursos recomendados cubre.

**Agregado**: Promedio por empleado  
**Objetivo**: > 0.60 (los 3 cursos cubren 60% del gap total)

<br>

## Reporte de Salida

<br>

Archivo: `data/reports/recommendation_evaluation.txt`

```
═══════════════════════════════════════════════════════════
COURSE RECOMMENDATION EVALUATION REPORT
Generated: 2026-04-11 10:39:00
═══════════════════════════════════════════════════════════

OVERALL METRICS
───────────────
Coverage:         92.3%  (462 / 500 employees)
Precision@3:      0.81   (2.4 relevant courses per employee)
Diversity Score:  0.74   (good topic spread)
Avg Gap Coverage: 0.63   (recommendations cover 63% of gaps)

SKILLS MOST RECOMMENDED
───────────────────────
1. software_data      (156 times) - 21.2%
2. analytics          (142 times) - 19.3%
3. leadership         (98 times)  - 13.3%
4. project_management (87 times)  - 11.8%
...

COURSES TOP 5 RECOMMENDED
─────────────────────────
1. "Python for Data Science" (edX) - 45 recommendations
2. "Advanced SQL" (Coursera) - 38 recommendations
3. "Leadership Essentials" (Udemy) - 35 recommendations
...

PROBLEMATIC SKILLS (coverage < 40%)
────────────────────────────────────
- systems: 28% coverage (only 2 courses found)
- domain_expertise: 35% coverage (niche courses needed)

RECOMMENDATIONS
───────────────
1. Expand course library for systems/infrastructure topics
2. Consider certifications (AWS, Azure)
3. Review fuzzy matching threshold if precision drops
```

<br>

## Cálculos Detallados

<br>

### Por Empleado

Para cada empleado `e` con gap `g_e`:

1. Recibir top-3 recomendaciones
2. Para cada recomendación:
   - Obtener skills del curso desde `course_skills_matrix`
   - Sumar `min(gap(e,s), course_score(c,s))` = value cubierto
3. Calcular `gap_coverage(e) = total_value_cubierto / sum(gaps)`

<br>

### Agregación Global

```python
precision@3 = mean([len([c for c in recs if is_relevant(c,e)]) / 3 
                    for e in employees])

coverage = count(employees with len(recs) > 0) / total_employees

diversity = 1 - (std_dev_topics / mean_topics)

gap_coverage = mean([gap_coverage(e) for e in employees])
```

<br>

## Umbrales de Calidad

<br>

| Métrica | Green | Yellow | Red |
|---------|-------|--------|-----|
| Coverage | > 85% | 75-85% | < 75% |
| Precision@3 | > 0.75 | 0.60-0.75 | < 0.60 |
| Diversity | > 0.70 | 0.50-0.70 | < 0.50 |
| Gap Coverage | > 0.55 | 0.40-0.55 | < 0.40 |

En rojo: Requiere revisión de parámetros (hiperparámetros, threshold de matching).

<br>

## Exportación de Resultados

<br>

- **CSV**: `data/final/course_recommendations.csv` (con scores)
- **TXT**: `data/reports/recommendation_evaluation.txt` (legible)
- **JSON** (futuro): Para integración con dashboards

<br>
