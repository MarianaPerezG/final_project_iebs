<br>

# Database Schema Design

<br>

La base de datos SQLite persiste datos clave para consultas rápidas desde la web app, evitando recargar CSVs grandes en memoria.

<br>

## Selección de SQLite

<br>

**Por qué SQLite:**
- No requiere servidor
- Persistence local en archivo único
- Queries rápidas con índices
- Suficiente para ~10k empleados

<br>

## Tablas Principales

<br>

### `skills_matrix`

```sql
CREATE TABLE skills_matrix (
  employee_number INTEGER PRIMARY KEY,
  job_role TEXT NOT NULL,
  analytics REAL,
  collaboration REAL,
  leadership REAL,
  business_functions REAL,
  project_management REAL,
  software_data REAL,
  systems REAL,
  domain_expertise REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Lectura rápida de skills por empleado desde detalle page  
**Índices**: PRIMARY KEY (employee_number)

<br>

### `course_recommendation` (metadata)

```sql
CREATE TABLE course_recommendation (
  course_id INTEGER PRIMARY KEY,
  title TEXT UNIQUE NOT NULL,
  provider TEXT,  -- "edX", "Udemy", "Coursera"
  level TEXT,
  subject TEXT,
  duration_hours INTEGER,
  indexed_at TIMESTAMP
);
```

**Propósito**: Búsqueda de metadata de cursos  
**Índices**: (provider, level), (subject)

<br>

### `gap_matrix` (opcional, para analytics)

```sql
CREATE TABLE gap_matrix (
  employee_number INTEGER,
  analytics REAL,
  collaboration REAL,
  ...
  PRIMARY KEY (employee_number),
  FOREIGN KEY (employee_number) REFERENCES skills_matrix(employee_number)
);
```

Opcional: Si se necesita acceso frecuente a gaps sin computar cada query.

<br>

## Relaciones

<br>

```
skills_matrix ←─── (employed)
     ↑
     │ gap_matrix.employee_number
     │
gap_matrix
```

No hay relaciones con course_recommendation (tabla de meta información).

<br>

## Consultas Frecuentes

<br>

```sql
-- Obtener skills de un empleado
SELECT * FROM skills_matrix WHERE employee_number = ?;
-- Índice: PRIMARY KEY es eficiente

-- Listar cursos por proveedor
SELECT * FROM course_recommendation WHERE provider = ?;
-- Índice: (provider, level)

-- Gap por empleado (si guardado)
SELECT * FROM gap_matrix WHERE employee_number = ?;
```

<br>

## Estrategia de Actualización

<br>

- **Cuando**: Final de cada ejecución de `run_pipeline()`
- **Cómo**: `DROP TABLE IF EXISTS` + `INSERT FROM CSV`
- **Transacciones**: Usar `BEGIN; ... COMMIT;` para batch insert
- **Performance**: ~5s para 10k empleados

<br>

## Compresión y Almacenamiento

<br>

- Ubicación: `src/config/database.db`
- Tamaño típico: ~2MB (10k empleados × 10 columnas)
- Backup: Copiar archivo .db antes de actualizar

<br>

## Considerar Futuro

<br>

- Si > 100k empleados: migrar a PostgreSQL
- Si > 10k queries/min: agregar caching (Redis)
- Si datos cambian frecuentemente: agregar versioning

<br>
