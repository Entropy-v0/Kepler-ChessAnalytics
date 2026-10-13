# Auditoría Técnica y Esquema de Estudio — Senior Data Engineer

**Proyecto:** Kepler-ChessAnalitic  
**Rol:** Auditoría Senior de Arquitectura e Ingeniería de Datos  
**Fecha:** Octubre 2026  
**Ubicación:** `docs/auditorias/auditoria.md`  

---

## 1. Resumen Ejecutivo y Diagnóstico Arquitectónico

El proyecto **Kepler-ChessAnalitic** ha sido diseñado como una plataforma analítica y motor ETL para el procesamiento y visualización del padrón oficial de jugadores de la FIDE (más de 770.000 registros). 

A diferencia de la mayoría de los proyectos exploratorios de ciencia de datos, este repositorio implementa prácticas avanzadas de ingeniería:
* **Arquitectura Medallion:** Flujo unidireccional por capas (`Raw` $\to$ `Interim` $\to$ `Processed` $\to$ `Marts`).
* **Ingesta en Streaming:** Uso de `xml.etree.ElementTree.iterparse` para no cargar el archivo XML descomprimido de 300+ MB en memoria de golpe.
* **Escritura Atómica en Parquet:** Implementación en `ParquetLoader` de archivos `.tmp` y renombrado atómico (`os.replace`) con lotes de 50.000 registros mediante PyArrow.
* **Capa Oro Desacoplada (Data Marts):** Pre-agregación determinista de 19 tablas Parquet optimizadas (< 200 KB cada una), permitiendo que la interfaz en Streamlit responda en menos de 50 ms consumiendo menos de 30 MB de RAM.

### Diagrama de la Arquitectura Actual

```mermaid
flowchart TD
    subgraph Ingesta["1. Capa Ingesta (Raw -> Interim)"]
        REMOTO[("FIDE ZIP Remoto")] -->|requests stream| RAW["data/raw/players_list_xml.zip"]
        RAW -->|iterparse streaming| PARSER["DataParser"]
        PARSER -->|Pydantic row-by-row| MODEL["FidePlayer"]
        MODEL -->|PyArrow chunked writer| INTERIM["data/interim/fide_players_bruto.parquet"]
    end

    subgraph Procesamiento["2. Capa Procesamiento (Interim -> Processed)"]
        INTERIM --> CLEANER["DataCleaner (Filtros & Deduplicación)"]
        CLEANER --> BUILDER["FeatureBuilder (Edad, Flags, Categorías)"]
        BUILDER --> PROC_ALL["data/processed/fide_players_all.parquet"]
        BUILDER --> PROC_ACT["data/processed/fide_players_active.parquet"]
    end

    subgraph Marts["3. Capa Oro (Processed -> Marts)"]
        PROC_ALL & PROC_ACT --> M_GLOB["global_marts.py"]
        PROC_ALL & PROC_ACT --> M_ELO["elo_marts.py"]
        PROC_ALL & PROC_ACT --> M_DEMO["demographic_marts.py"]
        PROC_ALL & PROC_ACT --> M_YOUTH["youth_marts.py"]
        PROC_ALL & PROC_ACT --> M_VEN["venezuela_marts.py"]
        M_GLOB & M_ELO & M_DEMO & M_YOUTH & M_VEN --> D_MARTS[("data/marts/*.parquet (19 tablas)")]
    end

    subgraph Consumo["4. Capa de Consumo y Servicios"]
        D_MARTS -->|@st.cache_data| SERVICES["app/service/ (*_service.py)"]
        SERVICES --> UI["app/pages/ (Streamlit Web)"]
        PROC_ACT -.->|Lectura exploratoria| NB["notebooks/ (Jupyter)"]
    end
```

---

## 2. Auditoría Técnica: Brechas y Buenas Prácticas Faltantes

A pesar de la sólida base existente, para elevar esta arquitectura al nivel de una plataforma de datos de producción corporativa existen 6 brechas críticas:

### Brecha 1: Idempotencia, Particionamiento Temporal y Time-Travel
* **Problema:** Las rutas de almacenamiento son estáticas (`players_list_xml.zip`, `fide_players_bruto.parquet`, `mart_*.parquet`). Como la FIDE publica actualizaciones mensuales, cada ejecución sobreescribe el estado previo, perdiendo la capacidad de auditar la evolución histórica de jugadores (delas de Elo, nuevas titulaciones o retiros).
* **Falta de Determinismo:** En `FeatureBuilder`, la edad se calcula por defecto usando `datetime.now().year`. Si se reprocesa un dataset de 2024 en el año 2026, el cálculo de las edades cambiará.
* **Mejores Prácticas:**
  * Particionamiento estilo Hive (`/snapshot=YYYY-MM/` o `/year=YYYY/month=MM/`).
  * Inmutabilidad de las capas Bronce y Plata.
  * Parámetro explícito de fecha de corte (`execution_date` o `snapshot_date`).

### Brecha 2: Contratos de Datos y Calidad (Data Contracts & Testing)
* **Problema:** Se valida fila por fila instanciando modelos Pydantic en un bucle Python (`IngestionController.validate_stream`). Esto impone un costo $O(N)$ severo en el intérprete de Python (770.000 iteraciones) y no valida el conjunto de datos de forma holística.
* **Riesgo:** Si el archivo fuente de la FIDE llega corrupto con solo 5.000 filas o columnas en blanco, el pipeline no aborta: procesa la anomalía, sobreescribe los Data Marts y rompe la aplicación web silenciosamente.
* **Mejores Prácticas:**
  * Validación declarativa de esquemas tabulares con **Pandera** o **Great Expectations**.
  * Detección de anomalías de volumen (ej. `count >= 700_000`), umbrales de nulos tolerables y rangos lógicos de valores (Elo entre 1000 y 3200).

### Brecha 3: Orquestación Avanzada y Grafos Dirigidos Acíclicos (DAGs)
* **Problema:** La orquestación reside en un script procedimental (`main.py`) con bloques condicionales `if stage in [...]`.
* **Limitaciones:**
  * No hay reintentos automáticos con retroceso exponencial (*exponential backoff*) ante fallas de red en `requests`.
  * Ejecución estrictamente secuencial: los generadores de Data Marts no dependen unos de otros, pero corren uno tras otro en un solo hilo.
  * Sin gestión de estado de ejecución (*state management* / *checkpoints*).
* **Mejores Prácticas:**
  * Modelado del flujo como un **DAG (Directed Acyclic Graph)** utilizando orquestadores modernos como **Prefect** o **Dagster**.
  * Ejecución paralela de tareas independientes.

### Brecha 4: DataOps, CI/CD y Reproducibilidad Hermética
* **Problema:**
  * Ausencia de integración continua (`.github/workflows/`).
  * Coexisten `requirements.txt` y `pyproject.toml` sin un archivo de bloqueo (*lockfile*) que fije las subdependencias con exactitud de hash.
  * No hay linters automáticos, formateadores ni verificación estática de tipos en pre-commit (`ruff`, `mypy`).
  * No hay contenedorización (`Dockerfile` / `docker-compose.yml`).
* **Mejores Prácticas:**
  * Gestión hermética de dependencias mediante **uv** (`uv.lock`).
  * Pipeline de CI en GitHub Actions que ejecute linters y pruebas en cada Pull Request.
  * Contenedor Docker multi-stage para asegurar paridad entre desarrollo y producción.

### Brecha 5: Observabilidad, Telemetría y Linaje de Metadatos
* **Problema:** Los registros de `loguru` se envían únicamente a `sys.stderr` y se destruyen al finalizar el proceso. No se recopilan métricas de ejecución.
* **Mejores Prácticas:**
  * Manifiesto de metadatos de auditoría al final de cada ejecución (ID de ejecución, registros ingresados, registros filtrados, duración por fase, tamaño en bytes).
  * Trazabilidad de linaje (*Data Lineage*): mapeo claro de qué versión del archivo fuente generó cada Data Mart.

### Brecha 6: Motor de Cómputo Analítico Vectorizado
* **Problema:** Pandas opera completamente en memoria, realiza copias implícitas (`.copy()`) y es monohilo.
* **Mejores Prácticas:**
  * Adopción de motores OLAP modernos dentro del proceso (*in-process OLAP*): **DuckDB** o **Polars**.
  * Reducción drástica del uso de memoria RAM mediante procesamiento vectorizado (SIMD) y optimización automática de consultas (*predicate pushdown*).

---

## 3. Esquema de Estudio Estructurado: Ruta Senior Data Engineer

Este plan de estudio organiza los conceptos teóricos y herramientas necesarias en 6 módulos secuenciales:

```
┌────────────────────────────────────────────────────────────────────────┐
│             RUTA DE ESTUDIO: DE PIPELINE A DATA PLATFORM               │
└────────────────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  [Módulo 1: Modelado &    [Módulo 2: Data Quality  [Módulo 3: Orquestación &
   Almacenamiento]          & Contratos de Datos]    DAGs Idempotentes]
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  [Módulo 4: Motores OLAP  [Módulo 5: DataOps,      [Módulo 6: Observabilidad
   (DuckDB / Polars)]       CI/CD & Docker]          & Metadatos / Linaje]
```

---

### Módulo 1: Almacenamiento Inmutable, Particionamiento e Idempotencia

* **Conceptos Teóricos:**
  * **Idempotencia en Pipelines:** Definición formal $f(f(x)) = f(x)$. Ejecutar una tarea $N$ veces debe producir el mismo resultado sin duplicaciones ni efectos secundarios.
  * **Particionamiento Hive-style:** Estructuración física de directorios (`/dataset/snapshot_date=YYYY-MM/part.parquet`) y poda de particiones (*partition pruning*).
  * **Snapshots vs Ingesta Incremental:** Cuándo persistir el estado completo y cuándo aplicar Change Data Capture (CDC).
  * **Dimensiones de Cambio Lento (SCD Tipo 2):** Modelado temporal con columnas de vigencia (`valido_desde`, `valido_hasta`, `es_actual`).
* **Lecturas Obligatorias:**
  * *Designing Data-Intensive Applications* (Martin Kleppmann) — Capítulos 1, 3 y 10.
  * Especificación del formato Apache Parquet (Metadata, Row Groups y Estadísticas de Diccionario).
* **Aplicación en Kepler:**
  * Parametrizar `settings.py` para admitir `--snapshot-date YYYY-MM`.
  * Guardar los archivos de las capas Raw e Interim bajo carpetas particionadas por fecha para conservar el histórico mensual.

---

### Módulo 2: Calidad de Datos, Esquemas y Contratos de Datos (Data Contracts)

* **Conceptos Teóricos:**
  * **Shift-Left Data Quality:** Validación temprana en la ingesta para evitar propagación de errores hacia las capas analíticas.
  * **Data Contracts:** Especificación formal entre productores y consumidores de datos (esquemas, restricciones semánticas y SLA).
  * **Detección de Deriva de Esquema (Schema Drift):** Estrategias para gestionar cambios inesperados en los tipos de datos o columnas de la fuente externa.
  * **Reglas de Calidad Declarativas:** Umbrales de nulos, valores únicos, tests de volumen y completitud.
* **Herramientas a Dominar:**
  * **Pandera:** Validación tipada y estadística de DataFrames en Python.
  * **Great Expectations / Soda Core:** Creación de suites de expectativas de datos.
* **Aplicación en Kepler:**
  * Sustituir el bucle fila a fila de Pydantic por un esquema de validación tabular con Pandera aplicado directamente sobre los bloques PyArrow o DataFrames de Pandas.
  * Implementar un test que aborte el pipeline si el volumen cae por debajo de 700.000 registros o si la tasa de nulos en `fideid` supera el 0%.

---

### Módulo 3: Orquestación Moderna y Grafos Dirigidos Acíclicos (DAGs)

* **Conceptos Teóricos:**
  * **Teoría de Grafos en Pipelines:** Dependencias topológicas, ordenación de tareas y paralelismo no bloqueante.
  * **Estrategias de Tolerancia a Fallos:** Reintentos con retroceso exponencial (*exponential backoff* con jitter) ante caídas de red.
  * **Gestión de Estado y Checkpoints:** Capacidad de reanudar la ejecución desde la tarea que falló sin repetir fases previas exitosas.
  * **Backfills Deterministas:** Reprocesamiento histórico reproducible mediante paso explícito de parámetros de fecha.
* **Herramientas a Dominar:**
  * **Prefect** o **Dagster** (orquestadores modernos centrados en Python y activos de datos, más livianos que Apache Airflow para este caso de uso).
* **Aplicación en Kepler:**
  * Transformar `src/main.py` en un flujo orquestado con Prefect/Dagster.
  * Configurar la generación paralela de `demographic_marts`, `elo_marts`, `youth_marts` y `venezuela_marts`.

---

### Módulo 4: Motores Analíticos Modernos (In-Process OLAP: DuckDB & Polars)

* **Conceptos Teóricos:**
  * **Procesamiento Vectorizado (SIMD) vs Ejecución por Filas:** Por qué procesar columnas en lotes en código nativo (C++/Rust) supera a Pandas en 10x-50x de velocidad.
  * **Optimización de Consultas:** *Filter/Projection Pushdown* para evitar leer columnas o filas no necesarias del archivo Parquet.
  * **Compartición de Memoria Zero-Copy:** Intercambio de datos entre PyArrow, DuckDB y Streamlit sin clonar estructuras en RAM.
* **Lecturas Obligatorias:**
  * *DuckDB in Action* (Mark Needham & Michael Hunger).
  * Documentación oficial de Polars: *Lazy API vs Eager API*.
* **Aplicación en Kepler:**
  * Reescribir los módulos de `src/marts/` sustituyendo las operaciones en memoria de Pandas por consultas SQL directas en DuckDB sobre los archivos Parquet procesados:
    ```python
    import duckdb
    duckdb.query("""
        SELECT country, AVG(rating) as avg_rating
        FROM 'data/processed/fide_players_active.parquet'
        GROUP BY country
    """).write_parquet("data/marts/mart_promedio_pais.parquet")
    ```

---

### Módulo 5: DataOps, CI/CD y Contenerización

* **Conceptos Teóricos:**
  * **Principios de DataOps:** Automatización del ciclo de vida del dato, pruebas continuas y entrega ágil de modelos y tablas analíticas.
  * **Reproducibilidad Hermética:** Eliminación de inconsistencias entre entornos de desarrollo y producción mediante contenedores.
  * **Integración Continua para Datos:** Pruebas unitarias de transformaciones, pruebas de contratos de datos y chequeo de estilo en cada commit.
* **Herramientas a Dominar:**
  * **uv:** Administrador de paquetes y dependencias en Rust con generación de `uv.lock`.
  * **Ruff & Mypy:** Linter, formateador y comprobador estático de tipos.
  * **Docker:** Multi-stage builds optimizados para aplicaciones Python.
  * **GitHub Actions:** Definición de flujos CI/CD.
* **Aplicación en Kepler:**
  * Generar un archivo de bloqueo reproducible con `uv lock`.
  * Configurar `.github/workflows/ci.yml` para ejecutar automáticamente `pytest` y `ruff check` en cada Pull Request.
  * Crear un `Dockerfile` que empaquete el pipeline ETL y el servidor de Streamlit.

---

### Módulo 6: Observabilidad, Telemetría y Linaje de Datos (Data Lineage)

* **Conceptos Teóricos:**
  * **Los 5 Pilares de la Observabilidad de Datos:** Frescura (*Freshness*), Volumen (*Volume*), Esquema (*Schema*), Distribución (*Distribution*) y Linaje (*Lineage*).
  * **Structured Logging:** Generación de eventos de log en formato JSON para agregación y monitoreo.
  * **Tablas de Auditoría de Ejecución:** Registro histórico de métricas de procesamiento por cada ejecución del pipeline.
* **Herramientas a Dominar:**
  * Estándar **OpenLineage**.
  * Métricas operativas con Prometheus o SQLite local.
* **Aplicación en Kepler:**
  * Crear un decorador o controlador de auditoría que al finalizar cualquier fase guarde un manifiesto `audit_run_YYYYMMDD_HHMMSS.json`:
    ```json
    {
      "run_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "timestamp": "2026-10-13T19:00:00Z",
      "stage": "marts",
      "duration_seconds": 3.42,
      "records_input": 436681,
      "marts_generated": 19,
      "status": "SUCCESS"
    }
    ```

---

## 4. Matriz de Priorización y Plan de Acción Progresivo

| Fase | Ámbito | Acción Técnica en Kepler | Impacto |
| :--- | :--- | :--- | :--- |
| **Fase 1** *(Inmediato)* | **DataOps & Tipado** | Bloquear dependencias con `uv.lock`, agregar `ruff` y crear workflow de GitHub Actions. | Elimina discrepancias de dependencias y asegura calidad en commits. |
| **Fase 2** *(Corto Plazo)* | **Data Quality** | Reemplazar Pydantic por **Pandera** en bloques de datos e implementar pruebas de volumen y nulos. | Acelera la ingesta 10x y protege la plataforma contra datos corruptos. |
| **Fase 3** *(Mediano Plazo)* | **Idempotencia & Partición** | Parametrizar fecha de ejecución (`snapshot_date`) y particionar carpetas `data/raw/` e `interim/`. | Permite análisis histórico y auditorías mensuales de jugadores. |
| **Fase 4** *(Avanzado)* | **Cómputo & DAGs** | Migrar cálculos de `src/marts/` a **DuckDB** y orquestar fases en un DAG concurrente (**Prefect**). | Reduce el uso de RAM al mínimo y paraleliza la construcción de tablas. |

---

## 5. Bibliografía y Recursos de Referencia

1. **Kleppmann, Martin.** *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems.* O'Reilly Media.
2. **Reis, Joe & Housley, Matt.** *Fundamentals of Data Engineering: Plan and Build Robust Data Systems.* O'Reilly Media.
3. **Needham, Mark & Hunger, Michael.** *DuckDB in Action.* Manning Publications.
4. **Dehghani, Zhamak.** *Data Mesh: Delivering Data-Driven Value at Scale.* O'Reilly Media.
5. **Kretz, Andreas.** *The Data Engineering Cookbook.* Repositorio de código abierto.

