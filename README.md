# 🎬 StreamView Analytics — Solución de Inteligencia de Negocios y Arquitectura de Datos

> **Evaluación Parcial N°1 (EP1) — Visualización de Datos (ADY1104)**  
> **Institución:** Duoc UC — Escuela de Informática y Telecomunicaciones  
> **Rol:** Equipo Consultor Senior en Business Intelligence y Arquitectura de Datos  
> **Destino:** Dashboard Analítico Interactivo en Tableau Desktop / Public

---

## 📌 1. Contexto de Negocio y Objetivos Estratégicos

**StreamView Analytics** es una plataforma internacional de streaming digital que busca optimizar la toma de decisiones basada en datos sobre su catálogo global unificado de películas y series. La organización requiere comprender el comportamiento de su contenido para fortalecer cuatro frentes estratégicos:

1. **Retención de Clientes:** Monitorear el ritmo y frescura con que se incorporan nuevos contenidos a la plataforma para evitar la fuga de suscriptores (*churn*).
2. **Nivel de Interacción (*Engagement*):** Identificar qué producciones y categorías generan tracción real, analizando la relación entre popularidad de consumo y volumen de interacción.
3. **Preferencias de Consumo de Contenido:** Conocer qué géneros, formatos (películas vs. series) y orígenes geográficos lideran la demanda.
4. **Experiencia y Calidad Percibida:** Medir la satisfacción del usuario mediante métricas de calificación confiables y no sesgadas por muestras ínfimas de votos.

---

## 🏛️ 2. Bitácora de Decisiones Arquitectónicas (ADR)

A partir de la auditoría técnica exhaustiva realizada sobre el pipeline original de preparación de datos, se aplicaron las siguientes correcciones arquitectónicas críticas:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                   FUENTES RAW (CSV)                     │
                  │   • netflix_movies_detailed_up_to_2025.csv (16K)        │
                  │   • netflix_tv_shows_detailed_up_to_2025.csv (16K)      │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                                               ▼
                  ┌─────────────────────────────────────────────────────────┐
                  │               LIMPIEZA, TIPADO Y CLAVES                 │
                  │   • Clave compuesta: content_key (resuelve colisiones)  │
                  │   • Poda selectiva: drop(rating, budget, revenue, dur)   │
                  │   • Restitución: country, date_added, vote_count, lang   │
                  └────────────────────────────┬────────────────────────────┘
                                               │
                        ┌──────────────────────┴──────────────────────┐
                        ▼                                             ▼
         ┌──────────────────────────────┐              ┌──────────────────────────────┐
         │     FEATURE ENGINEERING      │              │   TAXONOMÍA & EXPLODE        │
         │ • primary_country (Mapas)    │              │ • Armonización géneros       │
         │ • year_added, month_added    │              │   (Action & Adv -> Act, Adv) │
         │ • has_valid_votes flag       │              │ • Wide -> Long format        │
         │ • weighted_rating bayesiano  │              │                              │
         └──────────────┬───────────────┘              └──────────────┬───────────────┘
                        │                                             │
                        └──────────────────────┬──────────────────────┘
                                               │
                                               ▼
         ┌────────────────────────────────────────────────────────────────────────────┐
         │                        DATASETS PROCESADOS PARA BI                         │
         │                                                                            │
         │  1. streamview_catalog_clean.csv (31,991 filas | 1 fila = 1 título)        │
         │     -> Para KPIs, Mapas, Cohortes Temporales, Totales exactos              │
         │                                                                            │
         │  2. streamview_genres_bridge.csv (71,139 filas | 1 fila = 1 título-género) │
         │     -> Modelo Relacional (Relationships / Noodles) en Tableau              │
         │                                                                            │
         │  3. streamview_tableau_master.csv (71,139 filas | Desanidado plano)        │
         │     -> Conexión rápida como tabla única desanidada                         │
         └────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Modelado de Géneros: Abandono del Formato Horizontal (*Wide*) por Formato Desanidado (*Long*)
- **Problema detectado:** El pipeline original expandía la columna `genres` en 8 campos horizontales (`genre_1`, `genre_2`, …, `genre_8`).
- **Impacto negativo en Tableau:** 
  - Inhabilitaba los filtros interactivos nativos (para filtrar por *"Action"*, el usuario debía armar una fórmula compleja que evaluara 8 columnas).
  - Imposibilitaba la creación directa de gráficos de barras o treemaps por género sin recurrir a campos calculados pesados.
  - Generaba una matriz dispersa (*sparse matrix*) con más del 90% de valores nulos en `genre_5` a `genre_8`.
- **Decisión arquitectónica:** Se desanidaron los géneros mediante `explode` (formato *Long*), creando una relación normalizada 1-a-N. Se provee tanto una tabla puente (`streamview_genres_bridge.csv`) como una tabla maestra denormalizada (`streamview_tableau_master.csv`), permitiendo utilizar el motor de relaciones lógicas de Tableau (*Tableau Relationships*) sin duplicar el recuento de títulos en métricas agregadas globales.

### 2.2 Restitución de Columnas Críticas (Eliminadas Erróneamente)
La auditoría demostró que se habían eliminado dimensiones con alta densidad de datos válidos:
- **`country` (92.9% de datos válidos):** Restituida para habilitar mapas coropléticos y análisis geográfico de la producción. Además, se construyó el campo derivado `primary_country` para geocodificación automática en Tableau.
- **`date_added` (100% de datos válidos):** Restituida para análisis de series de tiempo, ritmo de incorporación mensual/anual y detección de estacionalidad.
- **`vote_count` (100% de datos válidos):** Restituida como dimensión indispensable de volumen, necesaria para ponderar las calificaciones y separar títulos populares de producciones marginales.
- **`language` (100% de datos válidos):** Restituida para segmentación lingüística y análisis de diversidad de catálogo.

### 2.3 Eliminación Justificada de Redundancias y Variables Espurias
- **`rating` vs. `vote_average`:** Se comprobó que `rating` y `vote_average` tenían exactamente los mismos valores numéricos en el 100% de los 32,000 registros (0 diferencias). Se eliminó `rating` para evitar confusión semántica y optimizar el almacenamiento.
- **`budget` y `revenue`:** Más del 70% de los registros figuraban en \$0 (valores ausentes codificados como 0) y las series de televisión carecían totalmente de esta variable. Se descartaron para evitar correlaciones espurias de rentabilidad.
- **`duration`:** Estaba 100% vacía en películas y era constante (`1 Seasons`) en el 100% de las series de TV, por lo que carecía de varianza analítica.

### 2.4 Resolución de Colisión de Identificadores (`show_id`)
- **Problema:** Existen **397 `show_id` duplicados** entre películas y series que apuntan a contenidos totalmente distintos (por ejemplo, el ID `45094` corresponde a la película *"Conviction"* y a la serie *"The Following"*).
- **Solución:** Se preservó y formalizó la clave primaria compuesta `content_key` (`movies_<id>` y `tv_shows_<id>`), garantizando integridad referencial estricta y evitando fusiones incorrectas en Tableau.

### 2.5 Tratamiento de Sesgos: Calificación Ponderada Bayesiana (*Weighted Rating*)
- **Problema:** El 14.2% del catálogo (4,555 títulos) registraba `vote_average = 0.0` debido a tener 0 votos. Paralelamente, más de 480 títulos tenían una calificación perfecta de `10.0` sustentada en solo 1 o 2 votos. Promediar directamente distorsionaba los rankings del negocio.
- **Solución:** Se implementó la fórmula bayesiana estándar de IMDb / TMDB:
  $$\text{WR} = \left(\frac{v}{v + m}\right) \cdot R + \left(\frac{m}{v + m}\right) \cdot C$$
  Donde:
  - $v = \text{vote\_count}$ (número de votos del título).
  - $R = \text{vote\_average}$ (calificación promedio original).
  - $m = 184.0$ (umbral mínimo de votos, percentil 70 de títulos calificados).
  - $C = 6.63$ (media global del catálogo calificado).
  - Si $v = 0$, `weighted_rating` se asigna como nulo (`null`), permitiendo a Tableau excluirlo automáticamente de los promedios de satisfacción.
  - Se incorporó el flag booleano `has_valid_votes` para filtrar interactivamente el catálogo calificado.

### 2.6 Armonización de Taxonomía de Géneros
Se normalizó la discrepancia de nombres entre películas y series:
- `"Action & Adventure"` $\rightarrow$ `Action`, `Adventure`
- `"Sci-Fi & Fantasy"` $\rightarrow$ `Science Fiction`, `Fantasy`
- `"War & Politics"` $\rightarrow$ `War`, `Politics`

---

## 📂 3. Estructura Profesional del Repositorio

Cumpliendo con los estándares de entrega de Duoc UC, el repositorio está estructurado de la siguiente manera:

```text
Visualizacion-de-datos-parcial/
│
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv    # Fuente cruda: películas
│   ├── netflix_tv_shows_detailed_up_to_2025.csv  # Fuente cruda: series
│   └── processed/                                # Datos transformados listos para Tableau
│       ├── streamview_catalog_clean.csv          # Catálogo maestro (1 fila = 1 título, 31,991 filas)
│       ├── streamview_genres_bridge.csv          # Tabla puente género (1 fila = 1 relación, 71,139 filas)
│       └── streamview_tableau_master.csv         # Tabla unificada desanidada (71,139 filas)
│
├── notebooks/
│   └── Parcial_Visualización_De_Datos.ipynb      # Pipeline reproducible documentado paso a paso
│
├── src/
│   └── data_preparation.py                       # Script Python modular de transformación y exportación
│
├── dashboard/                                    # Libro de trabajo y empaquetado de Tableau (.twbx)
│
├── images/                                       # Capturas del dashboard, arquitectura y storytelling
│
├── EP1_Instrucciones y Pauta EP1...pdf          # Pauta y rúbrica oficial de la evaluación
└── README.md                                     # Documentación técnica y guía de arquitectura
```

---

## 📊 4. Diccionario de Datos de los Archivos Procesados

### A. `streamview_catalog_clean.csv` (Nivel Grano: 1 fila por título único)

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `content_key` | String (PK) | Identificador compuesto único e inequívoco | `movies_10192` |
| `show_id` | Integer | Identificador numérico de la fuente original | `10192` |
| `type` | String | Formato de producción (`Movie` o `TV Show`) | `Movie` |
| `title` | String | Título oficial de la producción | `Inception` |
| `release_year` | Integer | Año de estreno original | `2010` |
| `date_added` | Date | Fecha de incorporación al catálogo de streaming | `2010-07-15` |
| `year_added` | Integer | Año de incorporación (para cohortes anuales) | `2010` |
| `month_added` | Integer | Mes de incorporación (1 a 12, estacionalidad) | `7` |
| `country` | String | País o países de origen (texto completo) | `United Kingdom, United States` |
| `primary_country` | String | País principal (optimizado para mapas en Tableau) | `United Kingdom` |
| `language` | String | Código de idioma original ISO (ej. `en`, `es`, `ja`) | `en` |
| `popularity` | Float | Índice de popularidad y engagement en la plataforma | `156.242` |
| `vote_average` | Float | Calificación media original otorgada por usuarios | `8.369` |
| `vote_count` | Integer | Cantidad total de votos registrados | `37119` |
| `has_valid_votes` | Boolean | Indica si el título tiene calificaciones reales | `True` |
| `weighted_rating` | Float | Calificación bayesiana ponderada (ajustada por volumen) | `8.36` |
| `genres_harmonized` | String | Géneros consolidados en una cadena legible | `Action, Science Fiction, Adventure` |

### B. `streamview_genres_bridge.csv` (Nivel Grano: 1 fila por relación título-género)

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `content_key` | String (FK) | Clave foránea que referencia al catálogo limpio | `movies_10192` |
| `genre` | String | Nombre normalizado del género individual | `Adventure` |

---

## 🚀 5. Guía de Integración y Construcción del Dashboard en Tableau

### Opción 1 (Recomendada — Modelo Dimensional en Tableau):
1. Abrir **Tableau Desktop / Tableau Public**.
2. Conectar a archivo de texto $\rightarrow$ seleccionar `streamview_catalog_clean.csv`.
3. Arrastrar `streamview_genres_bridge.csv` al lienzo lógico (*Logical Layer*).
4. Tableau creará automáticamente una relación (*Noodle*) vinculando ambos archivos mediante `content_key = content_key`.
5. **Ventaja:** Permite filtrar y agrupar por `genre` sin que el recuento total de títulos (`COUNTD(content_key)`) ni las sumas métricas se dupliquen al cambiar de nivel de detalle.

### Opción 2 (Conexión Directa a Tabla Única):
- Conectar directamente a `streamview_tableau_master.csv`.
- **Recomendación para métricas en Tableau:** Al calcular totales de títulos en vistas desanidadas, utilizar siempre `COUNTD([content_key])` en lugar de `SUM(Number of Records)` para evitar el sobreconteo por títulos multigénero.

---

## 🎨 6. Propuesta de Visualizaciones y KPIs (Alineada a Rúbrica Duoc UC)

En cumplimiento de los indicadores de evaluación **IE4 a IE10** de la pauta:

| Componente del Dashboard | Tipo de Gráfico / Representación | Dimensiones y Métricas | Justificación Perceptual y Cognitiva |
|---|---|---|---|
| **Cabecera de KPIs** | Tarjetas de Valor Único (*Big Numbers*) | Total Títulos, % Calificado, Rating Medio Ponderado, Popularidad Mediana | Jerarquía visual inmediata (IE4). Reduce la carga cognitiva inicial (IE6). |
| **Preferencia por Género** | Gráfico de Barras Horizontales Ordenadas o Treemap | Eje Y: `genre`, Eje X: `COUNTD(content_key)`, Color: `AVG(weighted_rating)` | Permite comparar frecuencias con precisión de longitud y evaluar calidad simultáneamente (IE5, IE7). |
| **Distribución Geográfica** | Mapa de Símbolos o Coropletas | Dimensión geográfica: `primary_country`, Color: `COUNTD(content_key)` | Representación espacial intuitiva del origen del contenido global (IE7). |
| **Evolución del Catálogo** | Gráfico de Líneas Temporal | Eje X: `date_added` (Mes/Año), Eje Y: `COUNTD(content_key)`, Detalle: `type` | Facilita la identificación de estacionalidad y ritmo de inversión histórica (IE7, IE10). |
| **Matriz de Calidad y Tracción** | Gráfico de Dispersión (*Scatter Plot*) | Eje X: `AVG(popularity)`, Eje Y: `AVG(weighted_rating)`, Tamaño: `vote_count` | Muestra qué contenidos son altamente populares y bien valorados frente a nichos sobrevalorados (IE6, IE9). |

### Criterios de Diseño Recomendados:
- **Paleta de Color:** Utilizar paletas categóricas sobrias (ej. Azul StreamView `#1f77b4` y Coral `#ff7f0e` para distinguir Películas de Series) y paleta divergente o secuencial continua para `weighted_rating`.
- **Contraste y Legibilidad:** Mantener fondos claros o grises neutros para asegurar alta legibilidad en proyecciones y pantallas ejecutivas.
- **Interactividad:** Configurar acciones de filtro al hacer clic en el mapa (`primary_country`) o en las barras de género (`genre`), sincronizando todos los paneles.

---

## ⚙️ 7. Reproducibilidad Técnica

Para replicar y ejecutar todo el pipeline de datos desde cero:

```bash
# 1. Clonar el repositorio
git clone https://github.com/ChenteDUOC/Visualizacion-de-datos-parcial.git
cd Visualizacion-de-datos-parcial

# 2. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 3. Ejecutar script de procesamiento automatizado
python src/data_preparation.py

# 4. Alternativamente, ejecutar el notebook interactivo:
# notebooks/Parcial_Visualización_De_Datos.ipynb
```

