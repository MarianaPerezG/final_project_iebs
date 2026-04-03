<br>

# Ajuste de Skill Scores

<br>

Todas las entradas de empleados en el dataset [*IBM HR Analytics Employee Attrition & Performance*](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) incluyen atributos que se utilizan para calcular los vectores de competencias, ajustados por empleado, que aparecen finalmente en la «skill matrix». Para obtener estos vectores nuevos, se parte de los vectores de competencias base de los puestos de trabajo. Las métricas del empleado están representadas en los atributos `Education` (nivel de estudios) y `PerformanceRating` (calificación del rendimiento). Según los valores registrados en estos, se pondera su influencia en las distintas competencias del rol para obtener el vector de competencias del empleado.

<br>

Valores permitidos en `Education`:

  - **1** (no degree, educación secundaria obligatoria o bachillerato)
  - **2** (associate's degree, técnico superior)
  - **3** (bachelor's degree, grado)
  - **4** (master's degree, máster)
  - **5** (doctorate, doctorado)

<br>

Valores permitidos en `PerformanceRating`:

  - **1** (insuficiente, no alcanza los objetivos mínimos)
  - **2** (mejorable, por debajo de lo esperado)
  - **3** (adecuado, cumple de manera competente)
  - **4** (destacado, aporta valor añadido)
  - **5** (excelente, supera sistemáticamente todos los objetivos)

<br>

Normalización centrada en cero de las métricas de los empleados:

  - $e = \frac{E - 3}{2}$, donde $e \in [-1, 1]$

  - $p = \frac{P - 3}{2}$, donde $p \in [-1, 1]$

<br>

Dividimos las competencias, según su naturaleza, en dos grupos principales, para aplicar el mismo peso a cada competencia del grupo:

  - Las competencias técnicas, o **hard skills**, incluyen `analytics`, `software_data`, `systems` y `domain_expertise`
  - Las competencias de gestión, o **soft skills**, incluyen `collaboration`, `leadership`, `business_functions` y `project_management`

<br>

El nivel de estudios pesa más en competencias técnicas y la calificación del rendimiento en competencias de gestión. Es decir, los pesos están invertidos en los dos grupos de competencias. Una apunta a credenciales formativas estáticas o estructurales, y la otra, a una evaluación del desempeño observable, más situacional o conductual. Esta distinción se puede plantear como habilidades metodológicas frente a interpersonales. Las primeras, orientadas al conocimiento, demandan capacidades para comprender, analizar y resolver problemas especializados, y las segundas, orientadas a las personas, demandan capacidades para trabajar con otros, coordinar esfuerzos y dirigir la actividad hacia objetivos organizativos.

<br>

  - Según el atributo `Education` ($w_E(s)$), si la competencia es una **soft skill** ($s \in \mathcal{S}$), se le asigna un **peso secundario** ($a$), y si es una **hard skill** ($\mathcal{H}$), se le asigna un **peso principal** ($b$).
  - Según el atributo `PerformanceRating` ($w_P(s)$), si la competencia es una **soft skill** ($s \in \mathcal{S}$), se le asigna un **peso principal** ($b$), y si es una **hard skill** ($\mathcal{H}$), se le asigna un **peso secundario** ($a$).

<br>

$$
w_E(s) = \begin{cases} a, & s \in \mathcal{S} \\ b, & s \in \mathcal{H} \end{cases}
\qquad
w_P(s) = \begin{cases} b, & s \in \mathcal{S} \\ a, & s \in \mathcal{H} \end{cases}
$$

<br>

Para establecer el factor de multiplicación que penaliza o bonifica la valoración de las competencias, se utilizan los siguientes pesos:

  - $a = 0.10$
  - $b = 0.20$

<br>

Estos valores generan un ajuste por competencia de hasta ±30 % en los extremos (E=5, P=5 y E=1, P=1), respecto al perfil base del rol, preservando la jerarquía de competencias definida por este.

<br>

$$
\text{score}_{\text{employee}}(r, s, E, P) = \text{clamp}_{[0, 5]} \bigl(\text{score}_{\text{role}}(r, s) \cdot M(s, E, P)\bigr),
\quad
M(s, E, P) = 1 + e w_E\bigl(g(s)\bigr) + p w_P\bigl(g(s)\bigr)
$$

<br>

```
         r: role
         s: skill
         E: «Education»
         P: «PerformanceRating»
M(s, E, P): multiplicador de ajuste
         e: normalización de «Education»
         p: normalización de «PerformanceRating»
      g(s): asignación de skill al grupo de soft o hard skills
       w_E: pesos según «Education»
       w_P: pesos según «PerformanceRating»
```

<br>
