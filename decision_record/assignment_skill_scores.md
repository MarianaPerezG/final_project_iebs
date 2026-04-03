<br>

# Asignación de Skill Scores

<br>

A continuación, se presenta el método empleado para calcular el peso que tienen los distintos tipos de habilidades en las funciones que desempeñan los roles extraídos del dataset [*IBM HR Analytics Employee Attrition & Performance*](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset). Aunque en el documento se muestren igualmente los roles del dataset [*Global AI Job Market Dataset (2010–2025)*](https://www.kaggle.com/datasets/terencekatua/global-ai-job-market-dataset-20102025), para mejorar el marco de observación, el procedimiento que se describe aplica exclusivamente al primero.

Cada rol se agrupa en familias ocupacionales canónicas, que sirven para establecer la puntuación base del vector de habilidades. Una vez que se conocen todos los títulos que definen los roles, se establece un ajuste semántico sobre cada vector base, sumando o restando influencia a habilidades específicas que representan los términos que componen el título.

<br>

## Familias ocupacionales

<br>

  1. Corporate Services (funciones corporativas): gestión de personas, talento y organización, centradas en desarrollo profesional, formación continua, cultura organizacional y procesos de recursos humanos.
  2. Commercial Strategy and Client Partnerships (desarrollo de negocio y relación con clientes): captación, gestión y atención de clientes, y actividad comercial y de cuenta.
  3. Applied Sciences and Specialized Technical Services (conocimiento técnico aplicado en contextos instrumentales o controlados): soporte técnico en entornos especializados, principalmente laboratorios.
  4. Research and Development (trabajo de investigación e innovación): validación y liderazgo en generación de conocimiento, experimentación e I+D.
  5. Business Operations and Execution (gestión de operaciones): coordinación de ejecución organizativa, supervisión de procesos y dirección de equipos.
  6. Product Strategy and Lifecycle (gestión de producto): definición de la visión, prioridades, funcionalidades y hoja de ruta de un producto.
  7. Decision Intelligence and Technical Advisory (análisis aplicado, inteligencia de negocio y asesoramiento técnico-conceptual): transformación de la información en diagnósticos, evaluación y apoyo en la toma de decisiones.
  8. Digital Solutions Engineering (construcción técnica de artefactos digitales): diseño, desarrollo e implementación de soluciones basadas en software, datos y aprendizaje automático.
  9. Technology Platforms and Infrastructure (arquitectura operativa de sistemas e infraestructura tecnológica): administración, integración, automatización y operación de plataformas, sistemas e infraestructura tecnológica.

<br>

Convención de identificadores en «job family» para la lógica interna:

  1. `corporate_services`
  2. `client_partnerships`
  3. `specialized_technical_services`
  4. `research_development`
  5. `business_operations`
  6. `product_lifecycle`
  7. `decision_advisory`
  8. `digital_engineering`
  9. `platform_infrastructure`

<br>

## Roles agrupados por familia ocupacional

<br>

Roles incluidos en *IBM HR Analytics Employee Attrition & Performance*:

| Job Family | Role |
|:---|:---|
| Corporate Services | Human Resources |
| Commercial Strategy and Client Partnerships | Healthcare Representative, Sales Executive, Sales Representative |
| Applied Sciences and Specialized Technical Services | Laboratory Technician |
| Research and Development | Research Director, Research Scientist |
| Business Operations and Execution | Manager, Manufacturing Director |

<br>

**Corporate Services**

  - *IBM HR Analytics Employee Attrition & Performance*: Human Resources

<br>

**Commercial Strategy and Client Partnerships**

  - *IBM HR Analytics Employee Attrition & Performance*: Healthcare Representative, Sales Executive, Sales Representative

<br>

**Applied Sciences and Specialized Technical Services**

  - *IBM HR Analytics Employee Attrition & Performance*: Laboratory Technician

<br>

**Research and Development**

  - *IBM HR Analytics Employee Attrition & Performance*: Research Director, Research Scientist
  - *Global AI Job Market Dataset (2010–2025)*: AI Researcher, Research Scientist

<br>

**Business Operations and Execution**

  - *IBM HR Analytics Employee Attrition & Performance*: Manager, Manufacturing Director
  - *Global AI Job Market Dataset (2010–2025)*: Operations Manager

<br>

**Product Strategy and Lifecycle**

  - *Global AI Job Market Dataset (2010–2025)*: Product Manager

<br>

**Decision Intelligence and Technical Advisory**

  - *Global AI Job Market Dataset (2010–2025)*: Business Analyst, Policy Analyst

<br>

**Digital Solutions Engineering**

  - *Global AI Job Market Dataset (2010–2025)*: Data Scientist, ML Engineer, Software Engineer

<br>

**Technology Platforms and Infrastructure**

  - *Global AI Job Market Dataset (2010–2025)*: Systems Engineer

<br>

## Criterios de puntuación

<br>

El grado de relevancia de una competencia, ajustado a un rol dado, se expresa en una escala ordinal de 0 a 5.

  - **0** (nula)
  - **1** (tangencial)
  - **2** (complementaria)
  - **3** (significativa)
  - **4** (determinante)
  - **5** (esencial)

<br>

Cada familia ocupacional debe tener una competencia esencial (5) o, en algunos casos, dos, para definir su identidad; puede tener hasta dos competencias determinantes (4); y las demás deben caer entre 0 y 3. Estas familias servirán de base para realizar los ajustes necesarios por cada puesto de trabajo incluido en ellas.

<br>

$$
\text{score}(r, s) = \text{clamp}_{[0, 5]}\bigl(B(f(r), s) + A(r, s)\bigr),
\quad
\text{clamp}_{[0, 5]}(x) = \max\bigl(0, \min(5, x)\bigr)
$$

<br>

```
             r: rol, o título del puesto de trabajo evaluado
             s: skill, o competencia global evaluada
          f(r): family(role), o familia ocupacional del rol
    B(f(r), s): base(family, skill), o puntuación base de la familia en esa skill
       A(r, s): adjustment(role, skill), o ajuste específico del rol
clamp(x, 0, 5): acota el valor al intervalo [0, 5]
```

<br>

Vector base de cada familia:

| job_family | collaboration | leadership | business_functions | analytics | project_management | software_data | systems | domain_expertise |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| corporate_services | 4 | 3 | 5 | 2 | 3 | 0 | 0 | 0 |
| client_partnerships | 4 | 1 | 5 | 1 | 2 | 0 | 0 | 1 |
| specialized_technical_services | 2 | 0 | 0 | 2 | 1 | 0 | 1 | 5 |
| research_development | 3 | 2 | 0 | 5 | 2 | 1 | 0 | 5 |
| business_operations | 4 | 3 | 1 | 2 | 5 | 0 | 2 | 1 |

<br>

Ajustes semánticos por título:

  - **−1** (negativo)
  - **+1** (medio)
  - **+2** (fuerte)

<br>

## 1. Ajuste jerárquico

<br>

**El título contiene «Director»**

  - `collaboration`: +1
  - `leadership`: +2
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: +1
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

**El título contiene «Manager»**

  - `collaboration`: 0
  - `leadership`: +1
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: +1
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

**El título contiene «Executive»**

  - `collaboration`: 0
  - `leadership`: +1
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: +1
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

## 2. Ajuste comercial

<br>

**El título contiene «Sales»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: +1
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

**El título contiene «Representative»**

  - `collaboration`: +1
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

## 3. Ajuste de investigación

<br>

**El título contiene «Research»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: +1
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: 0

<br>

**El título contiene «Scientist»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: +1

<br>

## 4. Ajuste instrumental

<br>

**El título contiene «Healthcare»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: +1

<br>

**El título contiene «Laboratory»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: +1
  - `domain_expertise`: +1

<br>

**El título contiene «Technician»**

  - `collaboration`: 0
  - `leadership`: −1
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: 0
  - `domain_expertise`: +1

<br>

**El título contiene «Manufacturing»**

  - `collaboration`: 0
  - `leadership`: 0
  - `business_functions`: 0
  - `analytics`: 0
  - `project_management`: 0
  - `software_data`: 0
  - `systems`: +1
  - `domain_expertise`: +1

<br>

## Vectores de habilidades por rol

<br>

Resultado del ajuste semántico:

| role | collaboration | leadership | business_functions | analytics | project_management | software_data | systems | domain_expertise |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Human Resources | 4 | 3 | 5 | 2 | 3 | 0 | 0 | 0 |
| Healthcare Representative | 5 | 1 | 5 | 1 | 2 | 0 | 0 | 2 |
| Sales Executive | 4 | 2 | 5 | 1 | 3 | 0 | 0 | 1 |
| Sales Representative | 5 | 1 | 5 | 1 | 2 | 0 | 0 | 1 |
| Laboratory Technician | 2 | 0 | 0 | 2 | 1 | 0 | 2 | 5 |
| Research Director | 4 | 4 | 0 | 5 | 3 | 1 | 0 | 5 |
| Research Scientist | 3 | 2 | 0 | 5 | 2 | 1 | 0 | 5 |
| Manager | 4 | 4 | 1 | 2 | 5 | 0 | 2 | 1 |
| Manufacturing Director | 5 | 5 | 1 | 2 | 5 | 0 | 3 | 2 |

<br>
