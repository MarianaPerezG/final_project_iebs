<br>

# Gap Matrix Formula

<br>

La «Gap Matrix» representa las brechas de competencias por empleado, calculadas como la diferencia entre el nivel objetivo (Target Matrix) y el nivel actual (Skill Matrix). Identifica qué habilidades necesitan desarrollo.

<br>

## Fórmula

<br>

$$
\text{gap}(e, s) = \max \Bigl( \text{target}(e, s) - \text{skill}(e, s), \, 0 \Bigr)
$$

<br>

Donde:

- **`gap(e, s)`**: brecha de habilidad (necesidad de desarrollo)
- **`target(e, s)`**: nivel objetivo definido en Target Matrix
- **`skill(e, s)`**: nivel actual en Skill Matrix
- **`max(x, 0)`**: solo se registran valores positivos

<br>

## Justificación del `max(x, 0)`

<br>

Se usa `max` porque:

1. **Interpretación**: El gap mide "qué debe desarrollarse", no sobrecalificación
2. **Recomendaciones**: Solo generamos cursos para cerrar brechas, no para rebajar nivel
3. **Simplificación**: Un empleado en objetivo o superior no necesita acción

<br>

## Ejemplos

<br>

| Empleado | Skill | Skill Score | Target Score | Gap | Interpretación |
|----------|-------|-------------|--------------|-----|----------------|
| E1 | analytics | 2.5 | 4.0 | 1.5 | Necesita desarrollo |
| E1 | leadership | 4.5 | 3.5 | 0.0 | Ya está por encima |
| E2 | software_data | 3.0 | 3.0 | 0.0 | En objetivo |
| E3 | collaboration | 2.0 | 4.5 | 2.5 | Gran brecha |

<br>

## Propiedades

<br>

- **Rango**: `[0, 5]` (hereda escala de matrices base)
- **Densidad**: Matriz dispersa (~60% ceros típicamente)
- **Suma gap**: Por empleado indica déficit total de desarrollo
- **Priorización**: Gaps ordenados por magnitud para recomendaciones

<br>
