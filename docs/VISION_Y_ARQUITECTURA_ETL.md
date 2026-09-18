# Visión y Arquitectura Integral ETL / Data Platform

**Proyecto:** Kepler-ChessAnalitic
**Objetivo Principal:** Migrar de un modelo acoplado (donde la app web procesa datos masivos) a una Arquitectura Medallion por capas, delegando el cómputo pesado al motor ETL en `src/`.

## 1. Reglas Arquitectónicas (Principio Rector)
> "Los Notebooks exploran; el Motor ETL ejecuta y produce; la Aplicación Web visualiza."

* **`notebooks/`:** Entorno estrictamente de lectura/exploración. Prohibida la escritura en entornos productivos (`data/marts/`, `data/processed/`).
* **`src/`:** Motor ETL determinista. Único responsable de generar Data Marts.
* **`app/`:** Aplicación Streamlit. Solo consume Data Marts (Capa Oro). Prohibido el uso de Pandas para cálculos complejos o Scipy en runtime.

## 2. Arquitectura por Capas (Medallion)
* **Capa 1 (Raw/Bronce) `data/raw/`:** Almacenamiento inmutable del XML comprimido descargado de FIDE.
* **Capa 2 (Interim/Plata) `data/interim/`:** Parseo por streaming (`iterparse`), validación Pydantic estricta y guardado atómico en Parquet.
* **Capa 3 (Processed/Master) `data/processed/`:** Limpieza centralizada, imputación y segmentación (activos vs. totales).
* **Capa 4 (Gold/Marts) `data/marts/`:** Sustituto de `data/dataWeb`. Tablas hiper-agregadas, listas para el consumo en $<50$ ms por Streamlit.

## 3. Diagrama de Flujo de Datos
```mermaid
flowchart TD
    RAW["players_list_xml.zip"] --> PARSER["DataParser (iterparse)"]
    PARSER --> INTERIM["fide_players_bruto.parquet"]
    INTERIM --> CLEANER["DataCleaner (Processed)"]
    CLEANER --> BUILDER["MartsBuilder (src/marts/)"]
    BUILDER --> MARTS["Capa Gold (Marts < 200KB)"]
    MARTS --> APP["Streamlit App"]