<br>

# Skill Demand Vector Aggregation

<br>

El vector de demanda se construye desde el dataset [*LinkedIn Job Postings (2023-2024)*](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings), agregando la frecuencia de skills por familia ocupacional. Representa "qué el mercado está pidiendo".

<br>

## Agregación por Nivel de Familia

<br>

Para cada familia, los skills se agrupan por:

1. **Mención explícita**: Skill listed explícitamente en job description
2. **Inferencia**: Skill predicho desde keywords en título
3. **Contexto**: Skill relacionada históricamente con familia

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

