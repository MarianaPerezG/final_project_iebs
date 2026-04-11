<br>

# Job Title Resolution

<br>

Los job titles del dataset [*LinkedIn Job Postings (2023-2024)*](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) no coinciden directamente con las familias ocupacionales canónicas. La resolución mapea títulos a familias usando dos estrategias en cascada.

<br>

## Estrategia: Lexical → Semantic

<br>

**Fase 1: Lexical Matching**

1. Normalizar title: convertir a minúsculas, remover puntuación, espacios múltiples
2. Buscar tokens exactos en diccionario estático de mappings
3. Si coincidencia exacta: retornar familia inmediatamente

**Diccionario Lexical (ejemplos):**

```
"research scientist" → research_development
"data scientist" → decision_advisory
"software engineer" → digital_engineering
"product manager" → product_lifecycle
"sales representative" → client_partnerships
```

<br>

**Fase 2: Semantic Matching**

1. Si no hay match lexical, usar embeddings (`SentenceTransformer`)
2. Comparar embedding del title contra embeddings de familias
3. Retornar familia con máxima similitud coseno (threshold ≥ 0.65)

<br>

## Scores Semánticos por Familia

<br>

Se entrenan embeddings para cada familia ocupacional:

- `corporate_services`: "human resources", "talent management", "organizational development"
- `client_partnerships`: "sales", "account management", "business development"
- `specialized_technical_services`: "laboratory", "technical support", "instrumental analysis"
- `research_development`: "research", "science", "innovation", "experimental"
- `business_operations`: "operations", "logistics", "manufacturing", "supply chain"
- `product_lifecycle`: "product manager", "product owner", "product strategy"
- `decision_advisory`: "business analyst", "intelligence", "advisory", "consultant"
- `digital_engineering`: "software", "developer", "engineer", "architecture", "full-stack"
- `platform_infrastructure`: "infrastructure", "operations", "systems", "platform", "devops"

<br>

## Fallback y Logging

<br>

Si score semántico < 0.65:
- Asignar a familia **por defecto** (`business_operations`)
- Loguear warning con confidence score
- Permitir override manual en configuración

<br>
