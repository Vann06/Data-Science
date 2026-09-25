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
│   ├── 01_preparacion_eneic.ipynb
│   └── 02_pipelines.ipynb
├── Transform_Data/                    # Parquet, métricas, modelos y gráficas
├── dockerfile
├── compose.yaml
├── docker-compose.yml                 # Configuración anterior; no recomendada
└── requirements.txt
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

### 02 pipelines

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

El notebook 02 se detiene con un mensaje explicativo si el notebook 01 todavía no ha generado `Transform_Data/personas_preparadas_2025`.

## Descargar los datos

Desde PowerShell:

```powershell
cd C:\Projects\Data-Science\L07_Spark_ML_Lib
python Data\descargar.py
```

El descargador no sobrescribe archivos existentes. Los Excel y los derivados están excluidos de Git por su tamaño.

## Entorno recomendado con Docker

El contenedor usa Python 3.11, Java 17 y PySpark 3.5.1. Primero abra Docker Desktop y espere a que el motor esté listo.

Construya la imagen:

```powershell
cd C:\Projects\Data-Science\L07_Spark_ML_Lib
docker build -f dockerfile -t l07-spark:3.5.1 .
```

Inicie JupyterLab con el laboratorio completo montado:

```powershell
$laboratorio = (Get-Location).Path

docker run --rm `
  --name l07-eneic-jupyter `
  -p 127.0.0.1:8888:8888 `
  --mount "type=bind,source=$laboratorio,target=/opt/app/laboratorio" `
  --workdir /opt/app/laboratorio `
  --env SPARK_LOCAL_IP=127.0.0.1 `
  --env PYTHONPATH=/tmp/labdeps `
  --entrypoint bash `
  l07-spark:3.5.1 `
  -lc "python -m pip install --target /tmp/labdeps openpyxl 'pandas>=2.2,<3' 'numpy<2' && jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/opt/app/laboratorio"
```

Abra la URL `http://127.0.0.1:8888/lab?token=...` mostrada en la terminal. Jupyter continuará ejecutándose mientras:

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
4. Abra `Notebooks/02_pipelines.ipynb`.
5. Use nuevamente **Restart Kernel and Run All Cells**.
6. Revise las tablas de métricas y la interpretación generada al final.

## Salidas de los pipelines

El notebook 02 genera:

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

Estos son modelos de selección entrenados con 2025T1–T3 y comparados sobre 2025T4. El conjunto 2026T1 permanece reservado y no se consulta en los pipelines documentados aquí.

## Criterios metodológicos

- Los modelos usan exactamente `edad`, `antiguedad`, `horas_semanales`, `nivel_educativo`, `categoria_ocupacional` y `dominio`.
- La etiqueta es `salario_mensual` en quetzales.
- No se utilizan identificadores, FACTOR, otros ingresos, salario por hora ni cluster como predictores.
- No se imputan salarios ni se recortan extremos.
- Las métricas principales no son ponderadas.
- Los resultados describen los registros analizados y no son estimaciones oficiales de la población guatemalteca.

Fuente de datos: Instituto Nacional de Estadística de Guatemala, Encuesta Nacional de Empleo e Ingresos Continua.
