<br>

# Heurística de la Target Matrix

<br>

La Target Matrix conserva las mismas dimensiones $n \times m$ que la Skill Matrix; ambas relacionan a los empleados con competencias.

<br>

  - Cada empleado hereda el nivel objetivo de las competencias, definido para su rol o familia
  - La demanda del mercado multiplica esta representación base
  - Los objetivos de empresa se suman como refuerzo a ciertas competencias

<br>

La demanda debe operar como multiplicador del perfil base. Si una competencia no pertenece a la identidad del rol, el mercado no debería forzar su inclusión arbitraria en él. Una demanda alta de un rol no convierte las competencias principales de ese rol en el objetivo de todos los demás.

Los objetivos de empresa deben incorporarse como término aditivo. Se usan para romper con los perfiles canónicos. La empresa puede querer que ciertos roles desarrollen competencias que no son centrales en su perfil.

La Target Matrix representa un nivel objetivo de dominio por lo que no debería alterar la escala 0–5. Si un empleado ya está en 5, en una competencia de la Skill Matrix, se quedará igualmente en 5 en la Target Matrix, y no habrá diferencial (o brecha).

<br>

$$
\text{target}(e, s) = \text{clamp}_{[0, 5]} \Bigl(\text{base}(f_e, s) \cdot (1 + \alpha \cdot \text{demand}(f_e)) + \beta \cdot \text{goal}(s)\Bigr)
$$

<br>

```
           e: employee
         f_e: rol o familia ocupacional del empleado
           s: skill
base(f_e, s): puntuación base del rol o la familia a la que pertenece ese empleado en esa skill
 demand(f_e): demanda del rol o la familia
     goal(s): importancia estratégica de esa skill para la empresa
           α: peso según «demand»
           β: peso según «goal»
```

<br>

  - $\alpha = 0.30$
  - $\beta = 0.50$

<br>

La escala del ranking se normaliza al intervalo [0, 1].

<br>

$$
\text{demand}(f) = 1 - \frac{\text{rank}(f) - 1}{K - 1}
$$

<br>

En este caso se emplean las familias ocupacionales, siendo $ \text{rank}(f) $ el puesto que ocupan en el ranking de demanda y $ K $ el número total de familias.

<br>

Posiciones del dataset *IBM HR Analytics Employee Attrition & Performance*:

  - **1** → 1.00 (primera)
  - **2** → 0.75 (segunda)
  - **3** → 0.50 (tercera)
  - **4** → 0.25 (cuarta)
  - **5** → 0.00 (quinta)

<br>

Según el factor de demanda, el mercado puede reforzar el valor base de una competencia hasta un +30 % como máximo.

<br>

$$
1 + \alpha \cdot \text{demand}(f) \in [1.00, 1.30]
$$

<br>

Según los intereses de una empresa, estos pueden incrementar hasta 1 punto, un máximo de 3 competencias.

<br>

$$
\beta \cdot \text{goal}(s) \in \{0.0, 0.5, 1.0\}
$$

<br>

Incremento por objetivos:

  - **0** → +0.0 (irrelevante)
  - **1** → +0.5 (importante)
  - **2** → +1.0 (esencial)

<br>
