# Mapeo de Skills de Cursos desde API a Global Skills

## Problema

Los cursos obtenidos de la API (edX) tienen asociadas skills en tres formatos diferentes:
1. **Associated Skills**: lista explícita de skills mencionadas en el curso
2. **Subject**: categoría o tema principal del curso (ej. "Data Science & Machine Learning")
3. **Title**: título del curso (ej. "Introduction to Python for Data Analysis")

Sin embargo, estos nombres de skills y temas no coinciden directamente con el conjunto de **global_skills** (habilidades estandarizadas) definidas en nuestro modelo RH. La tarea es mapear cada uno de estos elementos al conjunto de global skills para poder construir una matriz coherente que represente qué habilidades cubre cada curso.

## Solución: Mapeo Ponderado Multi-Componente

Para resolver this, implementamos un sistema de mapeo que combina **fuzzy matching** con **ponderación** de tres fuentes de información:

### 1. Normalización y Mapeo (Fuzzy Matching)

Usamos la librería `rapidfuzz` para realizar matching flexible entre texto de la API y global_skills:

```python
scores = [
    fuzz.ratio(text, skill),
    fuzz.partial_ratio(text, skill),
    fuzz.token_set_ratio(text, skill),
    fuzz.token_sort_ratio(text, skill),
]
```

Esto nos permite:
- Capturar coincidencias parciales ("machine learning" ↔ "ml")
- Ignorar orden de palabras ("learning machine" ↔ "machine learning")
- Manejar variaciones textuales

Cada componente (skills, subject, title) pasa por:
1. **Normalización**: expansión de abreviaturas, eliminación de caracteres especiales
2. **Scoring**: cálculo de similitud contra cada global_skill
3. **Agregación**: tomar la confianza máxima por skill

### 2. Los Tres Componentes y sus Confidencias

#### A) Associated Skills (Confianza Base)
- **Fuente**: Lista explícita de skills del curso en la API
- **Método**: `score_skills(api_skills) → Dict[global_skill → confidence]`
- **Interpretación**: Si el curso explícitamente lista una skill, es signal fuerte
- **Ejemplo**: Curso con skill "Python" → alta confianza en "programming", "software development"

#### B) Subject (Contexto Temático)
- **Fuente**: Categoría o tema del curso (ej. subject puede ser lista ["Data Science", "Machine Learning"])
- **Método**: `score_text(subject_item) → Dict[global_skill → confidence]` (agregado por máximo)
- **Interpretación**: El subject describe el ámbito general del curso; skills dentro de ese ámbito son probables
- **Ejemplo**: Curso en subject "Business Analytics" → mayor relevancia en "analytics", "business_functions"

#### C) Title (Señal Descriptiva)
- **Fuente**: Título del curso (ej. "Machine Learning for Business Intelligence")
- **Método**: `score_text(title_norm) → Dict[global_skill → confidence]`
- **Interpretación**: El título resume la propuesta de valor; captura skills clave del contenido
- **Ejemplo**: Título con "Leadership" → relevancia en skill "leadership"

### 3. Pesos Asignados: 70% Skills, 20% Subject, 10% Title

**Fórmula ponderada:**
$$r_{c,s} = 0.7 \times \text{skill\_conf}[s] + 0.2 \times \text{subject\_conf}[s] + 0.1 \times \text{title\_conf}[s]$$

#### Razonamiento

1. **70% Associated Skills (Primario)**
   - Los datos de "associated skills" son la información más directa y confiable
   - El curso está explícitamente etiquetado con estas habilidades
   - Reflejan la intención del diseñador del curso
   - Justificación: priorizar la información más específica y editorializada

2. **20% Subject (Contexto, Secundario)**
   - El subject proporciona contexto temático que enriquece el entendimiento
   - No es tan directo como skills etiquetadas, pero es editorializado
   - Ayuda a captar skills implícitas dentro del dominio (ej. "Data Science" → "analytics")
   - Justificación: contexto relevante pero no tan directo como skills explícitas

3. **10% Title (Señal Tercera, Tertiary)**
   - El título es a menudo marketing-driven y menos técnico
   - Puede introducir ruido (títulos creativos, amigables)
   - Pero aporta nuances que skills y subject no capturan
   - Justificación: señal adicional, pero con menor peso por su naturaleza menos estructurada

#### Alternativas Contempladas

- **100% Skills only**: pierde contexto temático que ayuda a la recomendación
- **Equal weighting (1/3, 1/3, 1/3)**: no diferencia entre data editorializada vs. marketing
- **Learning-based weighting**: requeriría datos pre/post de usuarios; no disponibles actualmente

### 4. Ejemplo Concreto

**Curso:** "Python for Data Science"
- **Associated Skills:** ["Python", "Data Analysis", "Pandas"]
- **Subject:** ["Data Science", "Programming"]
- **Title:** "Python for Data Science"

**Scoring por cada global_skill** (extracto):

| Global Skill | Skills(0.7) | Subject(0.2) | Title(0.1) | **Final** |
|---|---|---|---|---|
| programming | 0.95 | 0.60 | 0.85 | 0.70 × 0.95 + 0.20 × 0.60 + 0.10 × 0.85 = **0.88** |
| analytics | 0.85 | 0.70 | 0.40 | 0.70 × 0.85 + 0.20 × 0.70 + 0.10 × 0.40 = **0.76** |
| business_functions | 0.20 | 0.15 | 0.10 | 0.70 × 0.20 + 0.20 × 0.15 + 0.10 × 0.10 = **0.18** |
| leadership | 0.05 | 0.05 | 0.02 | 0.70 × 0.05 + 0.20 × 0.05 + 0.10 × 0.02 = **0.04** |

**Resultado:** El curso mapea fuertemente a "programming" (0.88) y "analytics" (0.76), débilmente a "business_functions" (0.18) y muy débil a "leadership" (0.04).

### 5. Implementación Técnica

**Ubicación del código:**
- `src/recommender/skill_mapper.py`: clases `score_skills()` y `score_text()`
- `src/recommender/create_recommendations_matrix.py`: orquestación de scoring y ponderación
- `src/recommender/skill_normalizer.py`: normalización de texto (expansión de abreviaturas)

**Flujo:**
1. API devuelve cursos con `associated_skills`, `subject`, `level`
2. Normalizamos cada componente (expansión, limpiezas)
3. Calculamos confidencias para cada global_skill
4. Combinamos con pesos (0.7, 0.2, 0.1)
5. Guardamos scores en rango [0, 1] con 2 decimales de precisión

### 6. Ventajas del Enfoque

✅ **Robustez:** múltiples fuentes reducen el riesgo de falsos negativos  
✅ **Flexibilidad:** pesos ajustables sin cambiar código core  
✅ **Explicabilidad:** cada componente contribuye de forma clara y cuantificable  
✅ **Escalabilidad:** funciona con cualquier conjunto de global_skills  
✅ **Precisión:** 2 decimales permiten granularidad sin sobre-precisión

### 7. Próximos Pasos para Mejora

- **Aprendizaje supervisado:** si obtenemos datos de usuarios pre/post, usar XGBoost/regresión para aprender pesos óptimos
- **Umbrales adaptativos:** usar percentiles de scores en lugar de cortes fijos
- **Prerequisitos dinámicos:** incorporar información de `prerequisites` en la selección de cursos
- **Priorización por JobLevel:** ponderar cursos según nivel de seniority del empleado
- **NLP avanzado:** usar embeddings (sentence-transformers) en lugar de fuzzy matching para mejor semántica

---

**Decisión grabada:** 2026-04-06  
**Equipo:** Data Science  
**Estado:** Implementado
