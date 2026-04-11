<br>

# Heurística de la Skill Matrix

<br>

La «Skill Matrix» es la representación base de competencias de los empleados, derivada del dataset [*IBM HR Analytics Employee Attrition & Performance*](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset). Relaciona cada empleado con un vector de 8 habilidades globales.

<br>

## Fórmula Base

<br>

$$
\text{skill}(e, s) = \text{clamp}_{[0, 5]} \Bigl( \text{base}(f_e, s) \cdot m_e + \Delta_{\text{title}}(e, s) \Bigr)
$$

<br>

Donde:

- **`skill(e, s)`**: puntuación de habilidad del empleado `e` en skill `s`
- **`base(f_e, s)`**: puntuación base de la familia ocupacional `f_e` en skill `s`
- **`m_e`**: multiplicador derivado de Education y PerformanceRating
- **`Δ_title(e, s)`**: ajuste semántico basado en palabras clave del job title
- **`clamp[0,5]`**: limita el resultado al rango válido

<br>

## Multiplicador por Empleado

<br>

El multiplicador combina dos métricas normalizadas (rango [-1, 1]):

$$
m_e = 1 + w_H \cdot e_n + w_S \cdot p_n
$$

Donde:

- **`e_n = (E - 3) / 2`**: education normalizado
- **`p_n = (P - 3) / 2`**: performance normalizado
- **`w_H`**: peso para hard skills (education)
- **`w_S`**: peso para soft skills (performance)

<br>

**Pesos por tipo de habilidad:**

- Hard skills (`analytics`, `software_data`, `systems`, `domain_expertise`): `w_H = 0.40`, `w_S = 0.20`
- Soft skills (`collaboration`, `leadership`, `business_functions`, `project_management`): `w_H = 0.15`, `w_S = 0.50`

<br>

## Ajuste Semántico por Título

<br>

El title job se tokeniza y se asignan pesos a palabras clave que afectan skills específicas:

- **"Director"** / **"Manager"**: `+0.5` a leadership, business_functions
- **"Research"**: `+0.3` a domain_expertise, analytics
- **"Developer"** / **"Engineer"**: `+0.5` a software_data, systems
- **"Scientist"**: `+0.4` a analytics, domain_expertise
- **"Sales"** / **"Representative"**: `+0.3` a collaboration, project_management

<br>

Estas palabras clave se buscan case-insensitively y se suman al valor final.

<br>

## Escala de Puntuación Base por Familia

<br>

| Family | analytics | collaboration | leadership | business_functions | project_management | software_data | systems | domain_expertise |
|--------|-----------|----------------|------------|--------------------|--------------------|----------------|---------|------------------|
| Corporate Services | 2.0 | 4.5 | 4.0 | 4.5 | 4.0 | 1.5 | 2.0 | 2.0 |
| Commercial Strategy | 2.5 | 4.5 | 3.5 | 4.0 | 3.5 | 1.0 | 1.5 | 2.5 |
| Specialized Technical | 3.0 | 3.0 | 2.0 | 2.5 | 3.0 | 3.5 | 3.5 | 4.0 |
| Research & Development | 4.5 | 3.0 | 3.0 | 2.0 | 2.5 | 3.0 | 2.5 | 4.5 |
| Business Operations | 3.0 | 4.0 | 4.0 | 4.5 | 4.5 | 2.0 | 2.5 | 2.5 |
| Product Strategy | 3.5 | 3.5 | 3.5 | 4.0 | 4.0 | 2.0 | 2.0 | 3.0 |
| Decision & Advisory | 4.0 | 3.5 | 3.0 | 3.5 | 3.5 | 2.5 | 2.0 | 3.5 |
| Digital Engineering | 3.0 | 3.0 | 2.5 | 2.5 | 3.5 | 4.5 | 4.0 | 3.5 |
| Platform Infrastructure | 2.5 | 2.5 | 2.5 | 2.5 | 3.0 | 4.5 | 4.5 | 3.0 |

<br>
