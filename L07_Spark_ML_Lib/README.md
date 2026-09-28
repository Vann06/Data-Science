# Laboratorio 7 Spark MLlib ENEIC

Este proyecto prepara las bases de Personas de la ENEIC, desarrolla el análisis exploratorio solicitado y construye dos pipelines de regresión con Spark 3.5.1. El flujo reserva el primer trimestre de 2026 para la evaluación final y evita usarlo durante la selección de modelos.

## Estructura

```text
L07_Spark_ML_Lib/
├── Data/
│   ├── descargar.py
│   ├── fuentes.json
│   └── *.xlsx                         # Descargados localmente, ignorados por Git
├── Notebooks/
│   ├── 01_preparacion_eneic.ipynb     # Actividades 1–3
│   ├── 02_segmentacion_kmeans.ipynb   # Actividad 4
│   ├── 03_pipelines.ipynb             # Actividades 5–6
│   └── 04_evaluacion_final.ipynb      # Actividades 7–8
├── Transform_Data/                    # Parquet, métricas, modelos y gráficas
├── dockerfile                         # Python 3.11 + Java 17 + dependencias
├── compose.yaml                       # Levanta JupyterLab con el laboratorio montado
└── requirements.txt                   # Versiones instaladas en la imagen
```

## Qué hace cada notebook

### 01 preparacion eneic

1. Lee individualmente los cinco Excel y sus diccionarios.
2. Conserva la procedencia y asigna el período calendario por archivo.
3. Homologa tipos y códigos y une 2025 con `unionByName`.
4. Audita dimensiones, faltantes, filtros y claves duplicadas.
5. Guarda por separado los conjuntos preparados de 2025 y 2026 en Parquet.
6. Calcula descriptivos, distribuciones, medianas, evolución trimestral y correlaciones de Pearson para 2025.

La primera ejecución puede tardar porque cada archivo contiene entre 49 mil y 52 mil registros y hasta 302 columnas. Los mensajes `Task of very large size` son advertencias de rendimiento y no significan por sí solos que la ejecución haya fallado.

### 02 segmentacion kmeans

Implementa la actividad 4:

- Compara tres escenarios: edad, antigüedad y horas; lo mismo más salario en quetzales; y lo mismo más log10 del salario.
- `VectorAssembler`, `StandardScaler` y `KMeans` dentro de un `Pipeline`, con semilla fija.
- Evalúa K = 2, 3, 4 y 5 con silhouette (`ClusteringEvaluator`), método del codo y tamaño del cluster más pequeño.
- Criterio de selección: K ≥ 3, ningún cluster menor al 5% y mayor silhouette.
- Describe cada cluster con medianas, salario y composición por educación, categoría ocupacional y dominio.
- Guarda el modelo en `Transform_Data/modelos/kmeans_segmentacion` y la asignación en `Transform_Data/segmentacion_kmeans_2025`.

### 03 pipelines

Implementa los puntos 5 y 6:

- Entrenamiento: `2025T1`, `2025T2` y `2025T3`.
- Validación: `2025T4`.
- Prueba final reservada: `2026T1`.
- Baseline ajustado con la media salarial del entrenamiento.
- `StringIndexer`, `OneHotEncoder` y `VectorAssembler` dentro de cada pipeline.
- Regresión lineal con estandarización interna y siete configuraciones de regularización.
- Random Forest con cinco combinaciones de árboles y profundidad, y semilla fija.
- MAE, RMSE y R² calculados sobre exactamente la misma validación.
- Métricas de entrenamiento y brechas de generalización para apoyar el análisis de sobreajuste.
- Selección por menor RMSE y guardado de los mejores `PipelineModel`.

### 04 evaluacion final

Implementa las actividades 7 y 8:

- Lee la configuración elegida por algoritmo de `seleccion_modelos_validacion.json` (notebook 03).
- Reentrena ambos pipelines con todo 2025 (T1–T4) y evalúa una sola vez en 2026T1, con baseline, sobre exactamente los mismos registros.
- MAE, RMSE y R² en prueba, comparados con los de validación 2025T4.
- Residuo = real − predicho (positivo = subestimación). Gráficos real vs predicho (y = x, escala lineal y log) y residuos vs predicho con una misma muestra de hasta 5,000 registros.
- MAE y error medio por nivel educativo y dominio, y por tramos de percentil del salario real, con todos los registros de prueba.
- Discusión final de todos los hallazgos.

Los notebooks 02, 03 y 04 se detienen con un mensaje explicativo si el notebook 01 todavía no ha generado `Transform_Data/personas_preparadas_2025`.

## Descargar los datos

Desde PowerShell:

```powershell
cd C:\Projects\Data-Science\L07_Spark_ML_Lib
python Data\descargar.py
```

El descargador no sobrescribe archivos existentes. Los Excel y los derivados están excluidos de Git por su tamaño.

## Entorno recomendado con Docker

El contenedor usa Python 3.11, Java 17 y PySpark 3.5.1; las versiones de las librerías están en `requirements.txt` (PySpark 3.5.1 requiere `pandas<3` y `numpy<2`). No es necesario instalar Java ni PySpark en Windows: los notebooks deben ejecutarse dentro del contenedor, no con un entorno virtual local.

Primero abra Docker Desktop y espere a que el motor esté listo. Luego, desde la carpeta del laboratorio:

```powershell
cd L07_Spark_ML_Lib
docker compose up --build
```

La primera vez construye la imagen `l07-spark:3.5.1` (unos minutos); después reutiliza la caché. La carpeta del laboratorio queda montada en `/opt/app/laboratorio`, así que los Excel de `Data/` son visibles y todo lo que se guarda en `Transform_Data/` aparece también en Windows.

Abra la URL `http://127.0.0.1:8888/lab?token=...` mostrada en la terminal. Una vez creada la `SparkSession`, la Spark UI está en `http://127.0.0.1:4040`. Para detener: `Ctrl+C` y luego `docker compose down`.

Jupyter continuará ejecutándose mientras:

- la terminal permanezca abierta;
- no se presione `Ctrl+C`;
- Docker Desktop siga funcionando.

El aviso `Skipped non-installed server(s)` sólo indica que no están instalados algunos servidores opcionales de autocompletado y no impide ejecutar Python o Spark.

## Orden de ejecución

1. Abra `Notebooks/01_preparacion_eneic.ipynb`.
2. Use **Kernel > Restart Kernel and Run All Cells**.
3. Confirme que se hayan creado:
   - `Transform_Data/personas_preparadas_2025/`
   - `Transform_Data/personas_preparadas_2026/`
   - `Transform_Data/manifiesto_ejecucion.json`
4. Abra `Notebooks/02_segmentacion_kmeans.ipynb` y use **Restart Kernel and Run All Cells**.
5. Abra `Notebooks/03_pipelines.ipynb` y use nuevamente **Restart Kernel and Run All Cells**.
6. Abra `Notebooks/04_evaluacion_final.ipynb` y use **Restart Kernel and Run All Cells** (requiere el JSON del notebook 03).
7. Revise las tablas de métricas y las interpretaciones generadas al final de cada notebook.

Los notebooks 02 y 03 sólo dependen de los Parquet del notebook 01; el 04 depende además del JSON de selección del 03.

## Salidas de los pipelines

El notebook 03 genera:

```text
Transform_Data/
├── comparacion_modelos_validacion.csv
├── configuraciones_regresion_lineal.csv
├── configuraciones_random_forest.csv
├── seleccion_modelos_validacion.json
└── modelos/
    ├── validacion_regresion_lineal/
    └── validacion_random_forest/
```

Estos son modelos de selección entrenados con 2025T1–T3 y comparados sobre 2025T4. El conjunto 2026T1 permanece reservado en el notebook 03 y sólo se utiliza en `04_evaluacion_final.ipynb`.

## Criterios metodológicos

- Los modelos usan exactamente `edad`, `antiguedad`, `horas_semanales`, `nivel_educativo`, `categoria_ocupacional` y `dominio`.
- La etiqueta es `salario_mensual` en quetzales.
- No se utilizan identificadores, FACTOR, otros ingresos, salario por hora ni cluster como predictores.
- No se imputan salarios ni se recortan extremos.
- Las métricas principales no son ponderadas.
- Los resultados describen los registros analizados y no son estimaciones oficiales de la población guatemalteca.

Fuente de datos: Instituto Nacional de Estadística de Guatemala, Encuesta Nacional de Empleo e Ingresos Continua.
