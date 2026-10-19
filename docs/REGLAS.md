# Reglas Oficiales de la FIDE y Criterios Analíticos del Proyecto Kepler

Este documento define las reglas reglamentarias de la **Federación Internacional de Ajedrez (FIDE)** contenidas en el padrón maestro mensual (`players_list_xml_foa.xml`) y explica las decisiones de ingeniería de datos adoptadas en **Kepler-ChessAnalitic** (`src/config/constants.py`, `src/processing/` y `src/analytics/`).

---

## 1. Identificador Único de Jugador (`fideid`)

### Regla FIDE
Cada jugador registrado ante la FIDE recibe un código único vitalicio (`<fideid>`). Aunque está compuesto por dígitos, **no es una magnitud cuantitativa**, sino un código estructurado en dos partes:
1. **Prefijo de federación de origen:** Los primeros dígitos identifican la federación nacional donde el jugador fue dado de alta por primera vez (por ejemplo, `44...` y `144...` corresponden a Colombia `COL`; `39...` y `139...` a Venezuela `VEN`; `41...` y `241...` a Rusia `RUS`). Si el jugador cambia posteriormente de federación (`<country>`), conserva su `fideid` original de por vida.
2. **Secuencia de registro:** Dígitos correlativos asignados al momento de la afiliación.

### Decisión de Implementación
* En `FidePlayer` (`src/models/player.py`) y `DataCleaner` (`src/processing/cleaner.py`), el campo `fideid` se almacena y normaliza como **cadena de texto (`str`)**.
* **Justificación:** Evita que funciones estadísticas como `df.describe()` calculen promedios o desviaciones estándar carentes de sentido sobre identificadores, y habilita el análisis directo por prefijos (`df["fideid"].str.startswith("44")`) para detectar migración o cambios de federación.

---

## 2. Modalidades de Juego y Sistema de Rating Elo

### Regla FIDE
La FIDE evalúa y publica mensualmente tres listas de Elo independientes por ritmo de juego:
1. **Ajedrez Clásico (`rating`):** Partidas con control de tiempo estándar (generalmente $\ge 60$ minutos por jugador, según categoría de Elo).
2. **Ajedrez Rápido (`rapid_rating`):** Partidas donde cada jugador dispone de más de 10 minutos y menos de 60 minutos (incremento incluido para 60 jugadas).
3. **Ajedrez Blitz (`blitz_rating`):** Partidas donde todo el juego debe completarse en 10 minutos o menos por jugador.

* **Piso reglamentario de Elo (`1400`):** Desde la reforma del reglamento de rating de la FIDE (vigente desde marzo de 2024), el rating mínimo oficial publicado en cualquiera de las tres listas es **`1400`**.
* **Valor `0` en el XML:** Cuando un jugador no posee Elo en una modalidad, el XML de la FIDE reporta `0` o etiqueta vacía.

### Decisión de Implementación
* Todo jugador que tenga `0` (o nulo) simultáneamente en las tres listas (`rating`, `rapid_rating`, `blitz_rating`) se descarta del padrón analítico bajo la regla `sin_rating`.
* En los jugadores con al menos un Elo válido, los valores `0` en las modalidades no evaluadas se convierten a **`NaN` (`Int16` nullable)** para no sesgar a la baja el cálculo de medias, medianas ni cuantiles.

---

## 3. Actividad Oficial FIDE (`activo_fide`) vs. Actividad Mensual (`activo_mes`)

El padrón mensual de la FIDE provee dos mecanismos distintos relacionados con la actividad de los jugadores: la etiqueta `<flag>` y los contadores de partidas `<games>`, `<rapid_games>` y `<blitz_games>`.

### 3.1. Qué significa `<flag>` y cómo se corrige `activo_fide`
En el XML de la FIDE, el campo `<flag>` puede tomar cuatro valores:
* `""` (vacío): Hombre activo según lista estándar FIDE.
* `"w"`: Mujer (*Woman*) activa según lista estándar FIDE.
* `"i"`: Hombre inactivo (*Inactive*).
* `"wi"`: Mujer inactiva (*Woman Inactive*).

#### Limitación estructural del `<flag>` FIDE (Paradoja de Simpson) y Solución
Por reglamento histórico de la FIDE, la bandera de inactividad (`i` / `wi`) se asigna cuando un jugador pasa **1 año sin jugar partidas evaluadas de Ajedrez Clásico**, pero **la FIDE solo audita esta bandera sobre los jugadores que poseen Elo Clásico (`rating.notna()`)**:
* Si un jugador **solo tiene Elo Rápido o Blitz (`rating.isna()`)**, la FIDE **jamás le asigna `flag='i'`**, incluso si jugó su único torneo rápido hace 8 años. Su `<flag>` permanece siempre vacío (`""` o `"w"`), por lo que si se evalúa únicamente `~flag.isin({'i', 'wi'})`, el **100%** de los jugadores sin Elo Clásico parecería "activo".
* **Efecto estadístico (Caso Colombia vs. Mundo):**
  * Entre los jugadores con Elo Clásico, Colombia tiene una tasa de actividad de **`34.4%`** frente al **`39.3%`** mundial.
  * Sin embargo, como en Colombia el **`43.4%`** del padrón solo tiene Rápido/Blitz (frente al **`28.3%`** mundial), incluir a todos los de `<flag>` vacío sin filtro inflaría artificialmente la tasa de Colombia al `62.9%` (superando el `56.5%` mundial).


### 3.2. Qué significan `<games>`, `<rapid_games>` y `<blitz_games>` (`activo_mes`)
* **Representan partidas individuales evaluadas en el mes, NO torneos:** Indican cuántas partidas individuales computaron para el cálculo de Elo durante el período mensual de la lista (últimos 30 días).
  * Si un jugador disputa un torneo suizo a 9 rondas contra rivales con Elo FIDE, su campo reflejará `9`.
  * Las partidas decididas por incomparecencia (*walkover* / *forfeit*) no se evalúan para Elo y **no suman** en estos campos.
  * A diferencia del rating, aquí el valor **`0` sí es un número real** (*"jugó 0 partidas evaluadas este mes"*), por lo que se normaliza como entero `int16` conservando el `0`.
* En `FeatureBuilder`, construimos:
  * **`total_games`**: `games + rapid_games + blitz_games` (volumen total de partidas evaluadas por el jugador en el mes).
  * **`activo_mes`**: `total_games > 0` (`bool`).

#### Utilidad analítica de `activo_mes` y `total_games`
1. **Comparación sin sesgo entre países y modalidades:** A diferencia de `<flag>`, los contadores `games`, `rapid_games` y `blitz_games` se registran por igual en los tres ritmos. Permiten medir qué federación mueve más jugadores activos en el mes y mayor volumen de partidas evaluadas.
2. **Detección de intensidad competitiva mensual:** Un jugador con un valor elevado en `total_games` (por ejemplo, $> 18$ o $> 25$ partidas en un solo mes) indica alta frecuencia de competencia (múltiples torneos jugados y evaluados en el mismo período mensual).

---

## 4. Sistema de Títulos Oficiales FIDE (`title`)

### Regla FIDE
El XML de la FIDE separa los títulos de tablero en dos campos (`<title>` y `<w_title>`) más un tercero para títulos arbitrales/organizativos (`<o_title>`):
* **Títulos Absolutos / Abiertos (`TITLES_OPEN_TOP`):**
  * `GM` (*Grandmaster* — Gran Maestro)
  * `IM` (*International Master* — Maestro Internacional)
  * `FM` (*FIDE Master* — Maestro FIDE)
  * `CM` (*Candidate Master* — Maestro Candidato)
* **Títulos Femeninos (`TITLE_WOMAN`):**
  * `WGM` (*Woman Grandmaster* — Gran Maestra Femenina)
  * `WIM` (*Woman International Master* — Maestra Internacional Femenina)
  * `WFM` (*Woman FIDE Master* — Maestra FIDE Femenina)
  * `WCM` (*Woman Candidate Master* — Maestra Candidata Femenina)

### Decisión de Implementación
1. **Fusión por jerarquía de prestigio (`TITLES_ELITE`):** Una jugadora puede poseer simultáneamente un título abierto en `<title>` (ej. `FM`) y un título femenino superior en `<w_title>` (ej. `WGM`), o viceversa (`IM` y `WGM`). `DataCleaner` unifica ambos campos en una única columna categórica ordenada `title` conservando el título de mayor rango según la jerarquía oficial de requisitos de Elo:
   $$\text{nt} < \text{WCM} < \text{WFM} < \text{CM} < \text{WIM} < \text{FM} < \text{WGM} < \text{IM} < \text{GM}$$
   Luego elimina la columna redundante `w_title`.
2. **Corrección determinista de anomalías de sexo:** Si un registro presenta por error de digitación `sex == "M"` pero posee un título exclusivo femenino (`WGM`, `WIM`, `WFM`, `WCM`), `DataCleaner` corrige automáticamente `sex = "F"`.

---

## 5. Edad Federativa y Categorías Formativas (`categoria`)

### Regla FIDE
En las competencias oficiales de la FIDE, la elegibilidad para categorías juveniles (**Sub 8, Sub 10, Sub 12, Sub 14, Sub 16, Sub 18 y Sub 20**) no se rige por la fecha exacta de cumpleaños del día del torneo, sino por el **año calendario** (edad que el jugador cumple al 31 de diciembre del año en curso):
$$\text{edad} = \text{año\_referencia} - \text{birthday}$$

### Decisión de Implementación
* **Cotas de validación (`DataCleaner` y `FeatureBuilder`):**
  * `MIN_BIRTH_YEAR = 1900`: Se rechazan registros sin año de nacimiento (`sin_birthday`), anteriores a 1900 (`birthday_anomalo`) o mayores/iguales al año de referencia (`birthday_futuro`).
  * `MAX_ACTIVE_AGE = 95`: Jugadores con edad $> 95$ años que conservan `activo_fide == True` por omisión de baja administrativa en su federación se excluyen del padrón operativo activo (`df_active`).
* **Clasificación (`AGE_CATEGORY_RULES` en `src/config/constants.py`):**
  * `Sub 8`: $\le 8$ años
  * `Sub 10`: $9\text{ a }10$ años
  * `Sub 12`: $11\text{ a }12$ años
  * `Sub 14`: $13\text{ a }14$ años
  * `Sub 16`: $15\text{ a }16$ años
  * `Sub 18`: $17\text{ a }18$ años
  * `Sub 20`: $19\text{ a }20$ años
  * `Absoluta`: $> 20$ años

---

## 6. Perfiles de Ritmo de Juego (`player_profile`)

Según la combinación booleana de tenencia de Elo (`(has_classic, has_rapid, has_blitz)` definidas en `PLAYER_PROFILE_RULES`), todo jugador del padrón limpio se clasifica en uno de **7 perfiles mutuamente excluyentes**:
1. `completo`: Posee Elo en las 3 modalidades (Clásico + Rápido + Blitz).
2. `clasico_rapido`: Posee Elo Clásico y Rápido, sin Blitz.
3. `clasico_blitz`: Posee Elo Clásico y Blitz, sin Rápido.
4. `rapido_blitz`: Posee Elo Rápido y Blitz, sin Clásico.
5. `especialista_clasico`: Posee únicamente Elo Clásico.
6. `especialista_rapido`: Posee únicamente Elo Rápido.
7. `especialista_blitz`: Posee únicamente Elo Blitz.

