<br>

# Data Validation Rules

<br>

Este documento define las validaciones, limpieza y tratamiento de problemas de datos en toda la pipeline.

<br>

## Validaciones por Módulo

<br>

### Skill Matrix

**Entrada:**
- Dataset: IBM HR Analytics
- Requeridos: `EmployeeNumber`, `JobRole`, `Education`, `PerformanceRating`
- Rango Education: `[1, 5]` (error si fuera de rango)
- Rango PerformanceRating: `[1, 5]`

**Limpieza:**
- Remover duplicados por `EmployeeNumber`
- Rellenar NaN en Education/Performance con mediana de grupo (por JobRole)
- Normalizar JobRole: strip whitespace, standarizar mayúsculas

**Salida:**
- Skill Matrix: valores en `[0, 5]`
- Validación: min=0.0, max=5.0 sin excepciones tras clamp

<br>

### Target Demand Skill Matrix (LinkedIn)

**Entrada:**
- Dataset: LinkedIn Job Postings
- Requeridos: `job_title`, `job_description`
- Esperado: ~100k registros mínimo

**Limpieza:**
- Remover postings con `job_title` vacío (logging)
- Remover duplicados por `job_title` + `company` (keep first)
- Tokenizar `job_description` y extraer skills vía NLP

**Tratamiento de edge cases:**
- Si job_title sin mapeo semántico: familiarizar a `business_operations`
- Si skill menciones < 5 veces en dataset: descartar (ruido)

**Salida:**
- Skill Demand Vector: valores en `[0, 1]`

<br>

### Company Goals

**Entrada:**
- CSV: `goal_id`, `goal` (text)
- Requerido: al menos 1 goal

**Validación:**
- Si archivo vacío o no existe: usar goals por defecto
- Si goals contienen caracteres inválidos (UTF-8): traducir a ASCII

**Limpieza:**
- Strip whitespace de cada goal
- Remover duplicados
- Máximo 20 goals (warning si excede)

<br>

## Validaciones Globales

<br>

### Integridad de Filepath

```
Si archivo no existe:
  - Loguear path esperado
  - Crear directorio padre si no existe
  - Retornar error con sugerencias
```

<br>

### Rango de Valores

```
Skill scores (0-5):
  - Si < 0: → 0 (clamp)
  - Si > 5: → 5 (clamp)
  - Si NaN: → interpolar vecinos (por skill)
  
Demand scores (0-1):
  - Si < 0: → 0
  - Si > 1: → 1
  - Si NaN: → 0 (sin demanda por defecto)
```

<br>

### Dimensionalidad

```
Skill Matrix: n_employees × (1 + 8 skills) = n × 9 mínimo
Target Matrix: misma dimensión que Skill Matrix
Gap Matrix: misma dimensión que Skill Matrix
```

<br>

## Logging de Anomalías

<br>

| Evento | Nivel | Acción |
|--------|-------|--------|
| Missing CSV | ERROR | Detener pipeline |
| Empleado sin role | WARN | Descartar empleado |
| Skill fuera rango | WARN | Aplicar clamp |
| < 80% datos válidos | ERROR | Detener |
| Encoding issue | WARN | Usar fallback ASCII |

<br>

## Tolerancia de Calidad

<br>

```
Skill Matrix: max 5% filas inválidas
Target Matrix: max 2% valores NaN (interpolar)
Gap Matrix: max 1% anomalías (log + continue)
```

Si se exceden estos umbrales, parar pipeline y reportar.

<br>
