<br>

# Skill Demand Vector Aggregation

<br>

El vector de demanda se construye desde el dataset [*LinkedIn Job Postings (2023-2024)*](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings), agregando la frecuencia de skills por familia ocupacional. Representa "qué el mercado está pidiendo".

<br>

## Pipeline de Agregación

<br>

```
LinkedIn Postings
       ↓
Mapear job_title → family
       ↓
Agrupar postings por family
       ↓
Contar skill mentions por family
       ↓
Normalizar frecuencias → [0, 1]
       ↓
Skill Demand Vector
```

<br>

## Fórmula de Demanda

<br>

$$
\text{demand}(s, f) = \frac{\text{count}(s, f)}{\text{max}_k(\text{count}(k, f))}
$$

<br>

Donde:

- **`demand(s, f)`**: demanda normalizada de skill `s` en familia `f` ∈ [0, 1]
- **`count(s, f)`**: número de postings en familia `f` que mencionan skill `s`
- **Normalización por familia**: permite comparabilidad entre tamaños de familia

<br>

## Agregación por Nivel de Familia

<br>

Para cada familia, los skills se agrupan por:

1. **Mención explícita**: Skill listed explícitamente en job description
2. **Inferencia**: Skill predicho desde keywords en título
3. **Contexto**: Skill relacionada históricamente con familia

<br>

**Ejemplo: Digital Engineering**

```
Postings: 1,250
Skills encontrados:
  → Python: 980 mentions → demand = 980/980 = 1.0
  → JavaScript: 750 mentions → demand = 750/980 = 0.76
  → AWS: 600 mentions → demand = 600/980 = 0.61
  → SQL: 850 mentions → demand = 850/980 = 0.87
```

<br>

## Agregación por Job Family

<br>

| Family | Skill Core | Demand Score | Top 3 Skills |
|--------|------------|--------------|--------------|
| digital_engineering | software_data | 0.92 | software_data (1.0), systems (0.85), analytics (0.72) |
| decision_advisory | analytics | 0.88 | analytics (1.0), business_functions (0.79), collaboration (0.65) |
| research_development | domain_expertise | 0.85 | domain_expertise (1.0), analytics (0.91), systems (0.60) |
| product_lifecycle | project_management | 0.78 | project_management (1.0), leadership (0.82), business_functions (0.71) |
| business_operations | business_functions | 0.82 | business_functions (1.0), leadership (0.88), collaboration (0.75) |

<br>

## Skill Core (Competencia Esencial)

<br>

La skill con mayor demanda en cada familia se designa **Skill Core**. Es la dimensión principal usada en la Target Matrix para multiplicar la base:

$$
\text{demand effect}(e, f_e) = \text{demand}(\text{core}(f_e), f_e)
$$

<br>

## Validaciones

<br>

- Mínimo 30 postings por familia para calcular demanda (evita ruido)
- Si demanda < 0.3, considerar como señal "débil" (logging)
- Excluir skills genéricas (ej. "communication" aparece en >80% postings)

<br>
