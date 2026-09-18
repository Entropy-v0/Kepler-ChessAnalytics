# Estructura de Directorios del Proyecto: Kepler-ChessAnalitic

Este documento detalla el árbol de directorios exacto del repositorio, especificando los directorios previamente existentes y los nuevos directorios incorporados para completar la arquitectura integral ETL por capas (Medallion Lakehouse).

---

## 1. Árbol de Directorios Exacto y Completo

```text
Kepler-ChessAnalitic/
├── app/                                 # Capa de Presentación (Frontend Streamlit)
│   ├── assets/                          # Recursos visuales estáticos (imágenes, logos, CSS)
│   ├── components/                      # Componentes visuales y utilidades de interfaz
│   │   ├── charts.py                    # Constructores de gráficos interactivos Plotly
│   │   └── theme.py                     # Constantes de diseño, paleta de colores y cabeceras
│   ├── pages/                           # Páginas multi-página de la aplicación
│   │   ├── 00_inicio.py                 # Portada y contextualización del proyecto
│   │   ├── 01_panorama_global.py        # Tablero de distribución mundial y mapa coroplético
│   │   ├── 02_distribucion_elo.py       # Análisis de densidades KDE, percentiles y títulos
│   │   ├── 03_demografia_genero.py      # Brecha de género, pirámide etaria y paridad
│   │   ├── 04_cohortes_juveniles.py     # Canteras mundiales y curvas biológicas Sub-8 a Sub-20
│   │   └── 05_venezuela.py              # Padrón venezolano, comparativas y buscador reactivo
│   ├── service/                         # Capa de Consumo y Acceso a Datos (DAL de Streamlit)
│   │   ├── data_loader.py               # Cargador exclusivo con caché (@st.cache_data)
│   │   ├── demographics_service.py      # Servicio analítico para Demografía y Género
│   │   ├── elo_service.py               # Servicio analítico para Distribución de Elo
│   │   ├── global_service.py            # Servicio analítico para Panorama Global
│   │   ├── venezuela_service.py         # Servicio analítico para Venezuela
│   │   └── youth_service.py             # Servicio analítico para Cohortes Juveniles
│   └── main.py                          # Entrada principal de la aplicación Streamlit
│
├── data/                                # Lago de Datos Local (Gobernanza Lakehouse)
│   ├── raw/                             # [Capa 1 - Bronce] Datos en crudo e inmutables
│   │   └── players_list_xml.zip         # Archivo comprimido oficial descargado de FIDE
│   ├── interim/                         # [Capa 2 - Plata] Parquet bruto tipado y validado
│   │   └── fide_players_bruto.parquet   # Stream XML parseado y validado por Pydantic
│   ├── processed/                       # [Capa 3 - Master] Padrón limpio y segmentado
│   │   ├── fide_players.parquet         # Padrón base limpio
│   │   ├── fide_players_active.parquet  # Jugadores activos (flag != 'i') (~437K)
│   │   ├── fide_players_all.parquet     # Padrón total válido (~776K)
│   │   └── fide_players_perceptil_local.parquet # Padrón con percentiles locales
│   ├── marts/                           # [Capa 4 - Oro] NUEVO: Data Marts para Streamlit (<200KB)
│   │   ├── .gitkeep
│   │   ├── mart_panorama_global.parquet # KPIs mundiales + Top federaciones + Mapa ISO3
│   │   ├── mart_distribucion_elo.parquet# Bins histograma + Coordenadas KDE (Clásico, Rápido, Blitz)
│   │   ├── mart_titulos_federacion.parquet # Matriz de títulos GM, IM, FM por federación
│   │   ├── mart_demografia_genero.parquet # Ratios de género + Pirámide etaria quinquenal
│   │   ├── mart_cohortes_juveniles.parquet# Curvas de nivel formativo y canteras mundiales
│   │   └── mart_venezuela.parquet       # Padrón curado de Venezuela (3.055 jugadores)
│   └── dataWeb/                         # [LEGADO - En transición] Tablas previas de notebooks
│       ├── cateogrias_juveniles_fed.parquet
│       ├── demografia_paises.parquet
│       ├── demografia_titulos_oficiales.parquet
│       ├── jugadores_ajedrez_VEN.parquet
│       └── ratings_globales.parquet
│
├── docs/                                # Documentación de Arquitectura y Referencia
│   ├── 01_VISION_Y_ARQUITECTURA_ETL.md  # Visión del sistema y reglas de gobernanza
│   ├── 02_DIAGNOSTICO_DEUDA_TECNICA.md  # Tracker de deuda técnica y cuellos de botella
│   ├── 03_ESTRUCTURA_DIRECTORIOS.md     # Este documento (Árbol de directorios oficial)
│   └── 04_ROADMAP_MIGRACION.md          # Fases secuenciales de implementación
│
├── notebooks/                           # Entorno de Exploración e Investigación (EDA)
│   ├── 00-limpieza.ipynb                # Exploración inicial de calidad y filtros
│   ├── 01-eda_general.ipynb             # Análisis univariado y bivariado general
│   ├── 02-demografia_edad_genero.ipynb  # Hipótesis de género, edad y cohortes
│   └── README.md                        # Guía de uso: Prohibida la escritura en marts/
│
├── research/                            # Bitácoras de Investigación y Diagnósticos Profundos
│   ├── ARQUITECTURA_Y_ESCALABILIDAD.md  # Análisis de escalabilidad y series temporales
│   ├── DIAGNOSTICO_DATAWEB_Y_ARQUITECTURA_ETL.md # Diagnóstico exhaustivo de datos y servicios
│   ├── EVALUACION_NOTEBOOKS_Y_PREGUNTAS_INVESTIGACION.md # Evaluación metodológica de notebooks
│   ├── EXPLICACION_ESTRUCTURA_DIRECTORIOS.md     # Explicación exhaustiva de cada carpeta
│   └── GUIA_02_DEMOGRAFIA_EDAD_GENERO.md         # Guía conceptual de demografía FIDE
│
├── scripts/                             # Scripts utilitarios y de automatización operativa
│   └── (scripts de mantenimiento / tareas puntuales)
│
├── src/                                 # Motor ETL Central (Producción de Datos)
│   ├── config/                          # Configuración y variables del entorno
│   │   ├── __init__.py
│   │   └── settings.py                  # Rutas base, logging y variables de entorno
│   ├── controllers/                     # Orquestadores de flujo de datos
│   │   ├── __init__.py
│   │   ├── ingestion_controller.py      # Orquesta descarga y parseo streaming (Raw -> Interim)
│   │   ├── processing_controller.py     # NUEVO: Orquesta limpieza y segmentación (Interim -> Processed)
│   │   └── marts_controller.py          # NUEVO: Orquesta la materialización de Data Marts (Processed -> Marts)
│   ├── ingestion/                       # Ingesta streaming de bajo consumo de RAM
│   │   ├── __init__.py
│   │   ├── dataParser.py                # Parser iterparse XML de memoria O(1)
│   │   ├── fideDownloader.py            # Descarga de red en chunks
│   │   └── parquetLoader.py             # Guardado atómico en chunks de 50.000 registros
│   ├── models/                          # Contratos y esquemas de validación
│   │   ├── __init__.py
│   │   └── player.py                    # FidePlayer (Modelo Pydantic v2)
│   ├── processing/                      # NUEVO: Limpieza centralizada y Feature Engineering
│   │   ├── __init__.py
│   │   ├── cleaner.py                   # Reglas de descarte y saneamiento de nulos
│   │   └── feature_builder.py           # Imputación de edad, categoría y flags
│   ├── marts/                           # NUEVO: Generadores analíticos de la Capa Oro
│   │   ├── __init__.py
│   │   ├── global_marts.py              # Genera mart_panorama_global
│   │   ├── elo_marts.py                 # Genera mart_distribucion_elo y mart_titulos
│   │   ├── demographic_marts.py         # Genera mart_demografia_genero
│   │   ├── youth_marts.py               # Genera mart_cohortes_juveniles
│   │   └── venezuela_marts.py           # Genera mart_venezuela
│   ├── analytics/                       # Módulos analíticos univariados preexistentes
│   │   ├── __init__.py
│   │   ├── univariateAnalyzer.py
│   │   └── univariateVisualizer.py
│   └── main.py                          # CLI unificado del pipeline ETL (Descarga -> Marts)
│
├── tests/                               # Suite de Pruebas Automatizadas
│   ├── __init__.py
│   ├── test_ingestion.py                # Tests para descarga y streaming
│   ├── test_processing.py               # Tests para reglas de negocio y limpieza
│   └── test_marts.py                    # Tests para consistencia de Data Marts
│
├── .env                                 # Variables de entorno locales
├── .gitignore                           # Exclusiones de Git (datos brutos, venv, pycache)
├── pyproject.toml                       # Gestión de dependencias y configuración de empaquetado
└── README.md                            # Presentación y guía de despliegue del proyecto
```

---

## 2. Balance de Directorios: Existentes vs. Incorporados

### A. Directorios Incorporados (Nuevos / Faltantes)

Los siguientes directorios fueron identificados como faltantes en la arquitectura del proyecto y han sido formalmente creados en el repositorio:

1. **`data/marts/`:**
   * **Propósito:** Alojar la **Capa Oro (Data Marts)**. Reemplaza operativamente a `data/dataWeb/`.
   * **Beneficio:** Almacena tablas hiper-optimizadas (<200 KB) consumidas directamente por Streamlit en $<50$ ms, eliminando la sobrecarga de 111 MB de datos en la memoria de la aplicación.
2. **`src/processing/`:**
   * **Propósito:** Centralizar la limpieza de datos, filtrado de inconsistencias, cálculo de edades federativas y asignación de categorías formativas (`Sub 8` a `Absoluta`).
   * **Beneficio:** Elimina la dependencia de notebooks para limpiar el archivo `fide_players_bruto.parquet`.
3. **`src/marts/`:**
   * **Propósito:** Contener los generadores especializados de cada Data Mart para la aplicación web.
   * **Beneficio:** Mueve el cómputo pesado de Scipy (curvas KDE sobre 60K puntos), cortes quinquenales (`pd.cut`) y cálculo iterativo de percentiles fuera de la aplicación Streamlit, ejecutándolo una sola vez durante el pipeline batch.

---

### B. Directorios Preexistentes y su Rol Consolidado

* **`app/`:** Aplicación Streamlit completa con componentes visuales, páginas y servicios.
* **`data/raw/`:** Almacenamiento inmutable del archivo ZIP descargado de la FIDE.
* **`data/interim/`:** Parquet bruto generado por streaming y tipado con Pydantic.
* **`data/processed/`:** Datasets maestros limpios (`fide_players_all.parquet`, `fide_players_active.parquet`).
* **`data/dataWeb/`:** Directorio legado con 5 archivos Parquet generados desde notebooks. Entra en fase de depreciación para dar paso a `data/marts/`.
* **`src/config/`:** Configuración global del sistema.
* **`src/controllers/`:** Controladores de orquestación.
* **`src/ingestion/`:** Módulos de descarga HTTP y parseo XML por eventos.
* **`src/models/`:** Modelo Pydantic `FidePlayer`.
* **`src/analytics/`:** Herramientas analíticas exploratorias.
* **`notebooks/`:** Entorno exclusivo para experimentación y EDA.
* **`research/`:** Bitácoras e informes técnicos de arquitectura.
* **`docs/`:** Documentación técnica y contratos del sistema.
* **`tests/`:** Suite de pruebas automatizadas.