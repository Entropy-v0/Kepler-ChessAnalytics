# Propuesta de Evolución, Arquitectura y Visión de Producto

**Proyecto:** Kepler-ChessAnalitic  
**Autor:** Entropy  
**Fecha:** Octubre 2026  
**Ubicación:** `docs/PROPUESTA_EVOLUCION_Y_ARQUITECTURA.md`

---

## 1. Resumen de Ideas y Visión de Producto

### 1.1 El Problema de la FIDE
El ecosistema oficial de la FIDE (`ratings.fide.com`) opera como un directorio telefónico estático de consulta puntual. Solo responde a la pregunta: *¿Quién eres y qué rating tienes hoy?*

FIDE **no ofrece**:
* Análisis longitudinal o temporal de la población de jugadores.
* Detección de velocidad y aceleración de rating en canteras juveniles ($\Delta \text{Elo}/\text{tiempo}$).
* Diagnóstico de deserción o abandono deportivo (*churn* post-18 años).
* Comparativas de cohortes y percentiles de desarrollo generacional.
* Segmentación de estilos y especializaciones de juego (clásico vs. rápido vs. blitz).

### 1.2 La Oportunidad de Kepler-ChessAnalitic
Kepler se concibe como una plataforma analítica y de inteligencia de datos sobre el ecosistema FIDE. Su ventaja competitiva (moat) no radica únicamente en procesar el mes en curso, sino en la **acumulación y comparación sistemática de snapshots mensuales** (Data Warehouse histórico del ajedrez mundial).

### 1.3 Casos de Uso y Clientes Potenciales
1. **B2G / Federaciones Nacionales y Comisiones de Ajedrez**:
   * Auditoría de rendimiento nacional y benchmarking frente a otros países.
   * Monitoreo de canteras y detección de fuga de talentos.
   * Criterios objetivos de selección para olimpiadas y torneos internacionales.
2. **B2B / Entrenadores de Élite y Academias Privadas**:
   * Herramienta de scouting de rivales y talentos emergentes.
   * Reportes mensuales de evolución deportiva de sus alumnos frente a la cohorte mundial.
3. **B2C / Jugadores y Familias**:
   * Proyección personalizada de títulos y percentil generacional ("A tus 13 años con 1700 Elo estás en el top 5% mundial de tu edad").

### 1.4 Estrategia de Crecimiento y Tracción ("Proof of Work")
Partiendo de cero contactos y sin capital de riesgo inicial:
* **Contenido como networking**: Publicación de hallazgos estadísticos de impacto en comunidades globales donde el análisis de datos se valora orgánicamente (Reddit `r/chess`, blogs oficiales de Lichess, #chesstwitter).
* **Adquisición directa por valor aportado**: Ofrecer reportes analíticos gratuitos a 5-10 entrenadores o clubes privados para validar el dolor de mercado y convertir en clientes recurrentes.
* **Financiamiento no dilutivo**: Postulación a fondos internacionales para creadores técnicos independientes (ej. *Emergent Ventures*, grants de comisiones FIDE para educación/desarrollo, GitHub Sponsors).

---

## 2. Posibles Cambios y Evolución en el Pipeline de Datos

Para soportar analítica temporal avanzada y productos desatendidos, el pipeline actual puede extenderse de la siguiente forma:

1. **Ingesta Multi-Snapshot Automatizada**:
   * Descarga programada (cron mensual) del archivo FIDE al inicio de cada mes.
   * Almacenamiento organizado por partición `data/raw/YYYY-MM/` e `data/processed/snapshot_date=YYYY-MM-01/`.
2. **Motor de Deltas y Series Temporales (`src/processing/delta_calculator.py`)**:
   * Cálculo automático de $\Delta \text{Elo}_{\text{clasico}}$, $\Delta \text{Elo}_{\text{rapido}}$, $\Delta \text{Elo}_{\text{blitz}}$ comparando el snapshot actual con $t-1$ y $t-12$ meses.
   * Detección de *momentum* o aceleración de rating (*Rating Velocity*).
3. **Módulo de Reportes Desatendidos (`src/reporting/`)**:
   * Generación de fichas analíticas en PDF o HTML estático por jugador, club o federación, aptas para entrega comercial sin necesidad de interacción web.

---

## 3. Integración Sin Streamlit: Arquitectura Web Fija y Desacoplada

### 3.1 Limitaciones de Streamlit para un Producto Final
Streamlit es una solución de primer nivel para **prototipado rápido y validación**, pero presenta restricciones para un SaaS multi-usuario comercial ("no es una web fija"):
* **Reejecución completa del script**: Cada interacción del usuario dispara la reejecución del script en Python.
* **Sobrecarga de memoria por sesión**: Cada usuario conectado mantiene estado en la memoria del servidor Python, encareciendo el escalado.
* **Falta de componentes web nativos**: Dificultades para crear experiencias móviles optimizadas, integraciones nativas de pasarelas de pago (Stripe, cripto) y autenticación con control de roles.

### 3.2 Arquitectura Propuesta: Desacoplamiento por Capas

Gracias a la refactorización a la arquitectura Medallion ya implementada en `src/`, el motor ETL y los Data Marts (`data/marts/`) son completamente independientes de la interfaz gráfica.

```
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE INGENIERÍA DE DATOS                │
│                                                             │
│  [FIDE XML] ──> Ingestión ──> Interim ──> Processed ──> ETL │
│                                                     │       │
│                                                     ▼       │
│                                           data/marts/*.parquet│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE SERVICIOS / API                     │
│                                                             │
│       FastAPI + DuckDB (Motor analítico en memoria)         │
│       - Consultas SQL ultrarrápidas (<15 ms) sobre Parquet  │
│       - Endpoints REST JSON seguros y cacheados             │
│       - Capa de autenticación JWT (Roles: Gratuito, Pro)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE PRESENTACIÓN (WEB FIJA)             │
│                                                             │
│       Frontend Moderno (Next.js / React o SvelteKit)        │
│       - Páginas estáticas y dinámicas (SSR / SSG)           │
│       - Componentes visuales interactivos (Tremor, Plotly)  │
│       - Responsive nativo (Mobile-first para teléfonos)     │
│       - Pasarela de pagos integrada                         │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Componentes de la Solución "Sin Streamlit"

1. **Capa de Almacenamiento Analítico (Data Marts / DuckDB)**:
   * Los Data Marts generados por `MartsController` se mantienen en formato Parquet.
   * Se utiliza **DuckDB** como motor de consulta embebido en el backend. DuckDB puede consultar directamente los archivos Parquet sin necesidad de cargarlos en una base de datos relacional tradicional (PostgreSQL), logrando tiempos de respuesta de milisegundos.

2. **Capa de Backend (FastAPI)**:
   * Framework ligero, asíncrono y de alto rendimiento en Python.
   * Endpoints especializados:
     * `GET /api/v1/kpis/globales`
     * `GET /api/v1/players/{fide_id}`
     * `GET /api/v1/rankings/youth-acceleration`
     * `GET /api/v1/federations/{fed_code}/benchmark`
   * Gestión de rate-limiting, caché HTTP y suscripciones.

3. **Capa de Frontend (Next.js / React)**:
   * Interfaz web fija, moderna y rápida, desplegable sin costo de servidor en plataformas como Vercel o Cloudflare Pages.
   * Biblioteca de componentes visuales (TailwindCSS + Tremor o Lucide Icons) para una apariencia profesional y responsive.
   * Autenticación simplificada con servicios como Supabase Auth o Clerk.

4. **Transición sin pérdida de trabajo**:
   * El código en `src/` permanece intacto.
   * La lógica de negocio encapsulada en `src/controllers/marts_controller.py` y `src/processing/` se reutiliza íntegramente.
   * El MVP en Streamlit puede mantenerse en paralelo para uso interno o demos rápidas mientras se desarrolla el frontend web definitivo.

