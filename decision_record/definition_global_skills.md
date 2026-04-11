<br>

# Definición de Global Skills

<br>

El objetivo es identificar los puntos débiles de empresas para sugerir formación específica a sus empleados. En una primera iteración, nos centraremos en un tipo concreto de competencias, presentes en el dataset [*IBM HR Analytics Employee Attrition & Performance*](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset). Aunque, igualmente, se ha utilizado de apoyo el dataset [*Global AI Job Market Dataset (2010–2025)*](https://www.kaggle.com/datasets/terencekatua/global-ai-job-market-dataset-20102025). Ambos pertenecientes al mercado corporativo, donde priman las capacidades digitales, de investigación, análisis, gestión y comunicación. Los roles que se evalúan son técnicos, científicos, analíticos y directivos. Todos ellos pueden codificarse en un conjunto de habilidades explícitas, su desempeño es fácilmente observable con KPIs y las carencias se pueden solventar con recapacitación. Esto permite construir una «Skill Matrix» (competencias que posee la empresa representadas por sus trabajadores) y una «Target Matrix» (competencias que se prevé que se mantengan relevantes a corto y medio plazo).

<br>

$$
\text{gap}(e, s) = \max\Bigl(\text{target}(e, s) - \text{skill}(e, s), \\:0\Bigr)
$$

<br>

```
e: employee
s: skill
```

<br>

Si inspeccionamos los puestos de trabajo que aparecen en *IBM HR Analytics Employee Attrition & Performance*, nos encontramos con lo siguiente:

  1. Healthcare Representative
  2. Human Resources
  3. Laboratory Technician
  4. Manager
  5. Manufacturing Director
  6. Research Director
  7. Research Scientist
  8. Sales Executive
  9. Sales Representative

<br>

Mientras que los puestos de trabajo en *Global AI Job Market Dataset (2010–2025)* son estos otros:

  1. AI Researcher
  2. Business Analyst
  3. Data Scientist
  4. ML Engineer
  5. Operations Manager
  6. Policy Analyst
  7. Product Manager
  8. Research Scientist
  9. Software Engineer
 10. Systems Engineer


<br>

Para alinear la semántica, es necesario agrupar los puestos de trabajo en familias ocupacionales canónicas y elaborar una taxonomía base de habilidades, que se mapearán con el dataset [*LinkedIn Job Postings (2023-2024)*](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings), empleado para calcular la relevancia de las competencias en el mercado.

Las competencias necesarias para desempeñar los trabajos del segmento del mercado laboral observado en los datasets se pueden agrupar en las siguientes categorías:

<br>

**Habilidades transversales**

  - Colaboración / Coordinación interfuncional
  - Gestión de stakeholders / Orientación al cliente
  - Liderazgo / Transferencia de conocimiento

<br>

**Habilidades de negocio**

  - Ventas consultivas / Negociación / Gestión de cuentas
  - Gestión de producto / Hoja de ruta
  - Gestión del talento / RR. HH.

<br>

**Habilidades analíticas**

  - Análisis de datos / Razonamiento estadístico
  - Investigación / Experimentación
  - Análisis de negocio / Definición y seguimiento de KPIs

<br>

**Habilidades de gestión**

  - Gestión de proyectos / Planificación
  - Mejora y transformación de procesos
  - Calidad / Compliance

<br>

**Habilidades técnicas**

  - Programación / Ingeniería de software
  - Gestión de bases datos
  - Sistemas / Cloud / Infraestructura
  - Automatización / Despliegue / MLOps

<br>

**Habilidades de dominio**

  - Conocimiento científico-técnico del sector
  - Operaciones de laboratorio / Entornos especializados

<br>

De aquí, podemos extraer la propuesta de competencias final para el sistema:

  1. `collaboration`: colaboración y coordinación
  2. `leadership`: liderazgo de equipos y desarrollo de capacidades
  3. `business_functions`: gestión comercial, de producto y talento
  4. `analytics`: análisis estratégico e inteligencia de negocio
  5. `project_management`: gestión de proyectos, procesos y transformaciones
  6. `software_data`: ingeniería de software y soluciones de datos
  7. `systems`: automatización y soluciones tecnológicas
  8. `domain_expertise`: especialización científico-técnica

<br>
