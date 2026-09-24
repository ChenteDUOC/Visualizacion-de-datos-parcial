# 📘 Guía Paso a Paso para Construir el Dashboard en Tableau
## StreamView Analytics — Evaluación Parcial EP1 (Duoc UC)

Esta guía detalla el procedimiento exacto, estante por estante y clic por clic, para construir el dashboard analítico en **Tableau Public** o **Tableau Desktop**, utilizando los datasets limpios ubicados en `data/processed/`.

---

## 📑 Índice de Construcción

1. [Conexión y Modelado de Datos](#1-conexión-y-modelado-de-datos)
2. [Configuración de Campos y Metadatos](#2-configuración-de-campos-y-metadatos)
3. [Construcción de las 5 Hojas de Trabajo](#3-construcción-de-las-5-hojas-de-trabajo)
   - [Hoja 1: Barras Horizontales — Distribución por Género](#hoja-1-barras-horizontales--distribución-por-género)
   - [Hoja 2: Mapa Mundial — Origen Geográfico](#hoja-2-mapa-mundial--origen-geográfico)
   - [Hoja 3: Línea Temporal — Evolución del Catálogo](#hoja-3-línea-temporal--evolución-del-catálogo)
   - [Hoja 4: Matriz Scatter Plot — Calidad vs. Popularidad](#hoja-4-matriz-scatter-plot--calidad-vs-popularidad)
   - [Hoja 5: Heatmap — Género vs. Década de Lanzamiento](#hoja-5-heatmap--género-vs-década-de-lanzamiento)
4. [Construcción de Tarjetas de KPIs (Cabecera)](#4-construcción-de-tarjetas-de-kpis-cabecera)
5. [Ensamblado del Dashboard Interactivo](#5-ensamblado-del-dashboard-interactivo)
6. [Configuración de Acciones e Interactividad](#6-configuración-de-acciones-e-interactividad)
7. [Construcción de la Historia (Data Storytelling - 18%)](#7-construcción-de-la-historia-data-storytelling---18)
8. [Exportación y Entrega](#8-exportación-y-entrega)

---

## 1. Conexión y Modelado de Datos

### Método Recomendado: Modelo Relacional Lógico (Star Schema / Relationships)

1. Abre **Tableau Public** o **Tableau Desktop**.
2. En la pantalla de inicio, bajo **A un archivo**, haz clic en **Archivo de texto**.
3. Navega a la carpeta del proyecto y selecciona:
   `data/processed/streamview_catalog_clean.csv`.
4. En el lienzo de la fuente de datos (la pantalla que se abre), verás la caja de `streamview_catalog_clean`.
5. En el panel izquierdo, bajo **Archivos**, arrastra `streamview_genres_bridge.csv` hacia el lienzo, soltándolo a la derecha de `streamview_catalog_clean`.
6. Tableau mostrará una línea ondulada (*fideo* o *relationship*).
7. En el cuadro de diálogo de relación emergente:
   - **Campo de catálogo:** `content_key`
   - **Campo de puente:** `content_key`
   - **Operador:** `=`
8. Cierra el cuadro de diálogo. Ahora el modelo está configurado en nivel de relación lógica. Esto garantiza que las métricas globales del catálogo no se dupliquen al filtrar por géneros.

> [!TIP]
> **Método Alternativo:** Si prefieres conectar una sola tabla plana sin relaciones, simplemente selecciona `streamview_tableau_master.csv`. Recuerda usar siempre `COUNTD([content_key])` para contar títulos.

---

## 2. Configuración de Campos y Metadatos

Antes de crear las hojas, verifica la tipología de datos en el panel izquierdo de cualquier hoja de trabajo:

1. **`primary_country`**:
   - Clic derecho sobre `primary_country` $\rightarrow$ **Rol geográfico** $\rightarrow$ **País o región**.
   - Verás que el icono cambia a un pequeño globo terráqueo 🌐.
2. **`date_added`**:
   - Asegúrate de que tenga el icono de calendario 📅 (tipo Fecha).
3. **`has_valid_votes`**:
   - Debe estar en la sección superior de **Dimensiones** (icono `T|F` o texto).
4. **`content_key`**:
   - Debe estar como **Dimensión** (icono `Abc`). Si está como medida, arrástrala a dimensiones.

---

## 3. Construcción de las 5 Hojas de Trabajo

---

### Hoja 1: Barras Horizontales — Distribución por Género
*Objetivo: Identificar los géneros con mayor volumen y su calificación promedio ponderada.*
*Rúbrica: IE4 (Jerarquía visual, 14%), IE5 (Atributos visuales, 16%), IE7 (Gráfico adecuado, 12%).*

1. **Renombrar Hoja:** Clic derecho en la pestaña inferior $\rightarrow$ Renombrar como `01_Generos_Barras`.
2. **Filas:** Arrastra el campo `genre` (de `streamview_genres_bridge`).
3. **Columnas:** Arrastra `content_key` (de `streamview_catalog_clean`).
   - Clic derecho en la píldora verde de `content_key` en Columnas $\rightarrow$ **Medida** $\rightarrow$ **Recuento (distinto)** (`COUNTD`).
4. **Ordenar:** Haz clic en el botón de orden descendente en la barra de herramientas superior (ícono de barras con flecha hacia abajo) para que el género con más títulos quede arriba.
5. **Color:** Arrastra `weighted_rating` a la tarjeta **Color** en la tarjeta de Marcas.
   - Asegúrate de que la agregación sea **Promedio**: clic derecho en la píldora en Color $\rightarrow$ **Medida** $\rightarrow$ **Promedio** (`AVG`).
   - Clic en **Color** $\rightarrow$ **Editar colores**:
     - Paleta: **Naranja-Azul divergente** o **Secuencial azul**.
     - Activa "Escalonada" con 5 o 6 pasos si deseas mayor contraste.
6. **Etiquetas:** Arrastra `COUNTD([content_key])` a la tarjeta **Etiqueta** para mostrar el número exacto al final de cada barra.
7. **Tooltip:** Clic en **Información sobre herramientas** y personaliza:
   ```text
   Género: <genre>
   Títulos en catálogo: <COUNTD(content_key)>
   Calificación Media Ponderada: <AVG(weighted_rating)>
   Popularidad Promedio: <AVG(popularity)>
   ```

---

### Hoja 2: Mapa Mundial — Origen Geográfico
*Objetivo: Visualizar la distribución espacial de la producción del catálogo.*
*Rúbrica: IE6 (Carga cognitiva intuitiva, 20%), IE7 (Datos espaciales, 12%).*

1. **Renombrar Hoja:** `02_Mapa_Mundial`.
2. **Generar Mapa:** Haz doble clic sobre `primary_country`. Tableau generará automáticamente:
   - `Longitud (generada)` en Columnas.
   - `Latitud (generada)` en Filas.
3. **Tipo de Marca:** En la tarjeta desplegable de Marcas, selecciona **Mapa**.
4. **Color:** Arrastra `content_key` a **Color** $\rightarrow$ Clic derecho $\rightarrow$ **Medida** $\rightarrow$ **Recuento (distinto)** (`COUNTD`).
   - Clic en **Color** $\rightarrow$ **Editar colores** $\rightarrow$ Paleta **Azul secuencial**.
5. **Filtro de Desconocidos:** Si en la esquina inferior derecha aparece un indicador gris `1 desconocido`:
   - Haz clic en él $\rightarrow$ **Filtrar datos** para ocultar el valor `Unknown`.
6. **Tooltip:**
   ```text
   País: <primary_country>
   Títulos producidos: <COUNTD(content_key)>
   Calificación promedio: <AVG(weighted_rating)>
   ```

---

### Hoja 3: Línea Temporal — Evolución del Catálogo
*Objetivo: Analizar la velocidad de incorporación de películas vs. series a lo largo del tiempo.*
*Rúbrica: IE7 (Series temporales, 12%), IE9 (Coherencia con retención, 20%), IE10 (Storytelling, 18%).*

1. **Renombrar Hoja:** `03_Evolucion_Temporal`.
2. **Columnas:** Arrastra `date_added`.
   - Clic derecho en la píldora de `date_added` $\rightarrow$ Selecciona el segundo **Mes** (el que tiene año, correspondiente al valor continuo: `Mes de mayo de 2015`).
3. **Filas:** Arrastra `content_key` $\rightarrow$ Clic derecho $\rightarrow$ **Medida** $\rightarrow$ **Recuento (distinto)**.
4. **Color:** Arrastra `type` a la tarjeta **Color**.
   - Asigna colores sobrios y con alto contraste:
     - `Movie`: Azul `#1f77b4`
     - `TV Show`: Coral / Naranja `#ff7f0e`
5. **Filtro de Fechas:** Arrastra `date_added` a la tarjeta **Filtros** $\rightarrow$ Selecciona **Rango de fechas** $\rightarrow$ Excluye fechas nulas si las hubiera.
6. **Tooltip:**
   ```text
   Mes / Año: <date_added>
   Tipo de contenido: <type>
   Títulos agregados: <COUNTD(content_key)>
   ```

---

### Hoja 4: Matriz Scatter Plot — Calidad vs. Popularidad
*Objetivo: Identificar 'Joyas Ocultas' (alta calidad, baja popularidad) y 'Éxitos Masivos' (alta calidad, alta popularidad).*
*Rúbrica: IE5 (Uso de canales múltiples, 16%), IE6 (Comprensión de cuadrantes, 20%), IE9 (Decisiones estratégicas, 20%).*

1. **Renombrar Hoja:** `04_Calidad_vs_Popularidad`.
2. **Filtro de Calidad Obligatorio:** Arrastra `has_valid_votes` a **Filtros** $\rightarrow$ Marca únicamente `Verdadero` (`True`). Esto elimina los 4,555 ceros que no tienen votos.
3. **Columnas (Eje X):** Arrastra `popularity` $\rightarrow$ Clic derecho $\rightarrow$ **Medida** $\rightarrow$ **Promedio** (o mantener a nivel de fila si se desagrega).
4. **Filas (Eje Y):** Arrastra `weighted_rating` $\rightarrow$ Clic derecho $\rightarrow$ **Medida** $\rightarrow$ **Promedio**.
5. **Detalle (Granularidad):** Arrastra `title` a la tarjeta **Detalle** en Marcas.
   *(Nota: Si hay demasiados puntos y Tableau se ralentiza, puedes agregar un filtro de `COUNTD(content_key)` o filtrar por top géneros/años).*
6. **Color:** Arrastra `type` a **Color**.
7. **Tamaño:** Arrastra `vote_count` a **Tamaño** (los títulos con más votos tendrán burbujas mayores).
8. **Líneas de Referencia (Cuadrantes):**
   - Ve a la pestaña **Análisis** (al lado izquierdo de Datos).
   - Arrastra **Línea de referencia**:
     - Hacia la tabla en eje `popularity`: promedio global.
     - Hacia la tabla en eje `weighted_rating`: promedio global (6.63).
   - Esto divide visualmente el gráfico en 4 cuadrantes estratégicos.

---

### Hoja 5: Heatmap — Género vs. Década de Lanzamiento
*Objetivo: Mostrar la evolución histórica de los géneros en el catálogo.*
*Rúbrica: IE4 (Organización en matriz, 14%), IE7 (Cruce categórico-temporal, 12%).*

1. **Renombrar Hoja:** `05_Heatmap_Genero_Decada`.
2. **Campo Calculado de Década:**
   - Clic derecho en el panel de datos $\rightarrow$ **Crear campo calculado**:
     - Nombre: `Decada`
     - Fórmula: `STR(INT([release_year] / 10) * 10) + "s"`
3. **Filas:** Arrastra `genre` (de `genres_bridge`).
4. **Columnas:** Arrastra el campo calculado `Decada`.
5. **Tipo de Marca:** Selecciona **Cuadrado**.
6. **Color:** Arrastra `weighted_rating` a **Color** $\rightarrow$ **Medida** $\rightarrow$ **Promedio**.
   - Editar colores $\rightarrow$ Paleta **Rojo-Verde divergente** o **Naranja-Azul divergente**.
7. **Etiqueta:** Arrastra `content_key` a **Etiqueta** $\rightarrow$ **Medida** $\rightarrow$ **Recuento (distinto)** para ver el número de producciones en cada celda.

---

## 4. Construcción de Tarjetas de KPIs (Cabecera)

Crea 4 o 5 hojas pequeñas individuales para los números clave:

1. **KPI 1 - Total Títulos:**
   - Hoja nueva: `KPI_Total_Titulos`.
   - Marca: **Texto**.
   - Arrastra `content_key` a **Texto** $\rightarrow$ `COUNTD`.
   - Clic en Texto $\rightarrow$ Formatea con tamaño de fuente grande (24pt, Negrita).
   - Etiqueta debajo: "Títulos en Catálogo".
2. **KPI 2 - Películas:**
   - Filtro: `type = Movie`.
   - Texto: `COUNTD([content_key])` $\rightarrow$ "Películas".
3. **KPI 3 - Series:**
   - Filtro: `type = TV Show`.
   - Texto: `COUNTD([content_key])` $\rightarrow$ "Series".
4. **KPI 4 - Calificación Ponderada:**
   - Texto: `AVG([weighted_rating])` (formato 2 decimales: `6.63`) $\rightarrow$ "Rating Promedio".
5. **KPI 5 - Cobertura de Votos:**
   - Texto: `85.7%` $\rightarrow$ "% Con Calificaciones Válidas".

---

## 5. Ensamblado del Dashboard Interactivo

1. Haz clic en el ícono de **Nuevo Dashboard** (pestaña inferior con cuadrícula).
2. En el panel izquierdo de Dashboard:
   - **Tamaño:** Selecciona **Automático** o define **Fijo (1920 × 1080)** para asegurar que no se distorsione en presentaciones.
3. **Estructura de Contenedores:**
   - Arrastra un **Contenedor Vertical** al lienzo.
   - En la parte superior, agrega un cuadro de texto para el título:
     `STREAMVIEW ANALYTICS — DASHBOARD ESTRATÉGICO DE CONTENIDOS`.
   - Debajo del título, agrega un **Contenedor Horizontal** con las 5 tarjetas de KPIs lado a lado.
   - En la sección media, agrega un **Contenedor Horizontal**:
     - Lado izquierdo: `01_Generos_Barras`.
     - Lado derecho: `02_Mapa_Mundial`.
   - En la sección inferior, agrega otro **Contenedor Horizontal**:
     - Lado izquierdo: `03_Evolucion_Temporal`.
     - Lado derecho: `04_Calidad_vs_Popularidad`.

---

## 6. Configuración de Acciones e Interactividad

Para que el evaluador pueda interactuar fluidamente:

1. En el menú superior de Tableau: **Dashboard** $\rightarrow$ **Acciones...**
2. Clic en **Agregar acción** $\rightarrow$ **Filtrar...**
   - **Nombre:** `Filtrar por Género`
   - **Hojas de origen:** Marcar `01_Generos_Barras`.
   - **Ejecutar acción con:** **Seleccionar** (clic).
   - **Hojas de destino:** Marcar todas las demás hojas.
   - **Borrar la selección:** **Mostrar todos los valores**.
3. Repetir para el Mapa (`02_Mapa_Mundial`) como origen de filtro.
4. **Filtros Globales Visibles:**
   - Haz clic en la hoja `01_Generos_Barras` dentro del dashboard $\rightarrow$ Clic en la flecha desplegable de la esquina $\rightarrow$ **Filtros** $\rightarrow$ `type`.
   - Configura el filtro como **Lista desplegable múltiple**.
   - En el menú del filtro: **Aplicar a hojas de trabajo** $\rightarrow$ **Todas las que usen esta fuente de datos**.

---

## 7. Construcción de la Historia (Data Storytelling - 18%)

La rúbrica asigna un **18% a la narrativa visual (IE10)**. Tableau cuenta con el módulo específico **Story**:

1. Clic en el botón **Nueva Historia** (ícono de libro abierto en la barra inferior).
2. **Punto de Historia 1:**
   - Título de la pestaña: `1. Panorama Global del Catálogo`.
   - Arrastra el Dashboard completo.
   - Agrega un cuadro de texto descriptivo: *"El catálogo cuenta con 31,991 títulos equilibrados en 50% películas y 50% series. El 85.7% posee calificaciones válidas con un rating bayesiano medio de 6.63."*
3. **Punto de Historia 2 (Clic en 'En blanco' para nuevo punto):**
   - Título: `2. Concentración por Géneros vs. Calidad`.
   - Arrastra `01_Generos_Barras`.
   - Narrativa: *"Drama y Comedia dominan en volumen de títulos, pero producciones de Animación y Documental logran calificaciones ponderadas significativamente superiores."*
4. **Punto de Historia 3:**
   - Título: `3. Expansión Geográfica`.
   - Arrastra `02_Mapa_Mundial`.
   - Narrativa: *"Estados Unidos concentra la mayor producción, pero mercados asiáticos (Japón, Corea del Sur, India) muestran un crecimiento acelerado en series con alta tracción."*
5. **Punto de Historia 4:**
   - Título: `4. Dinámica de Incorporación Temporal`.
   - Arrastra `03_Evolucion_Temporal`.
   - Narrativa: *"A partir de 2020 se observa una aceleración en la adición de contenidos, con picos estacionales que coinciden con trimestres de renovación de suscripciones."*
6. **Punto de Historia 5:**
   - Título: `5. Conclusiones y Recomendaciones Estratégicas`.
   - Arrastra `04_Calidad_vs_Popularidad`.
   - Narrativa: *"Recomendación accionable: Focalizar adquisiciones en el cuadrante de 'Joyas Ocultas' (alto rating, baja popularidad) mediante campañas de descubrimiento personalizado."*

---

## 8. Exportación y Entrega

1. **Guardar en Tableau Public:**
   - Menú **Archivo** $\rightarrow$ **Guardar en Tableau Public como...**
   - Inicia sesión con tu cuenta gratuita de Tableau Public.
   - Asigna el nombre: `StreamView_Analytics_Dashboard_EP1`.
   - Copia la URL pública generada para incluirla en el informe ejecutivo PDF.
2. **Guardar Archivo Local:**
   - Menú **Archivo** $\rightarrow$ **Exportar libro de trabajo empaquetado...**
   - Guarda el archivo con extensión `.twbx` dentro de la carpeta `dashboard/` de este proyecto.

