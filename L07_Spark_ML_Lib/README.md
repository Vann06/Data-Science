# Laboratorio 7: Spark MLlib — ENEIC

El notebook `Notebooks/01_preparacion_eneic.ipynb` cubre los ejercicios recibidos:
1. Carga, armonización y calidad de datos.
2. Estadística descriptiva y exploración.
3. Correlaciones de Pearson.

Incluye respuestas conceptuales e interpretaciones numéricas generadas desde los resultados.
Las instrucciones de clustering y regresión aún están pendientes de recibir.

## Organización

- `Data/`: cinco bases de Personas y cinco diccionarios originales. `fuentes.json` registra las URL del INE; `descargar.py` recupera archivos faltantes sin sobrescribirlos.
- `Transform_Data/`: Parquet separados de 2025 y 2026, auditorías, CSV, gráficos y manifiesto de ejecución con huellas SHA-256.
- `Notebooks/`: notebook, exportación HTML tras ejecutarlo y utilidades de reproducción.

## Docker existente: revisado, sin modificaciones

`dockerfile` usa Python 3.11, Java 17 y PySpark 3.5.1, adecuados para la guía.
No instala `openpyxl`. `docker-compose.yml` sólo monta `working_dir` y `notebooks`;
no monta `Data` ni `Transform_Data`. También existe el `compose.yaml` de la preparación
anterior: no conviene invocar Compose sin indicar qué archivo se quiere usar.
Todos estos archivos se conservan tal como los dejó el usuario.

Para ejecutar sin modificar Docker, abrir Docker Desktop y, en PowerShell desde esta
carpeta, utilizar la imagen disponible `spark_practica-1-pyspark:latest`:

```powershell
$laboratorio = (Get-Location).Path
docker run --rm --name l07-eneic-ejecucion --mount "type=bind,source=$laboratorio,target=/opt/app/laboratorio" --workdir /opt/app/laboratorio --env SPARK_LOCAL_IP=127.0.0.1 --env PYTHONPATH=/tmp/labdeps --entrypoint bash spark_practica-1-pyspark:latest -lc "python -m pip install --target /tmp/labdeps openpyxl 'pandas<3' 'numpy<2' && python Notebooks/ejecutar_laboratorio.py"
```

Las dependencias adicionales se instalan sólo en `/tmp/labdeps` del contenedor temporal.
No se cambia la imagen ni Python en Windows. El contenedor desaparece al terminar;
los resultados quedan en la carpeta montada. Se necesita red para esas dependencias.
Si la imagen no existe en otro equipo, construirla con el Dockerfile existente:

```powershell
docker build -f dockerfile -t spark_practica-1-pyspark:latest .
```

Para abrir Jupyter de forma interactiva con los datos montados:

```powershell
$laboratorio = (Get-Location).Path
docker run --rm --name l07-eneic-jupyter -p 127.0.0.1:8888:8888 --mount "type=bind,source=$laboratorio,target=/opt/app/laboratorio" --workdir /opt/app/laboratorio --env SPARK_LOCAL_IP=127.0.0.1 --env PYTHONPATH=/tmp/labdeps --entrypoint bash spark_practica-1-pyspark:latest -lc "python -m pip install --target /tmp/labdeps openpyxl 'pandas<3' 'numpy<2' && jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/opt/app/laboratorio"
```

Abrir la URL local con token mostrada en consola. Si 8888 está ocupado, cambiar el puerto
del host, por ejemplo `-p 127.0.0.1:8889:8888`.
El `requirements.txt` previo describe una alternativa con Spark 3.5.7; no se usa en estos
comandos, que respetan Spark 3.5.1 de la imagen del curso.

## Contenido y decisiones

Se verifican dimensiones y procedencia; se unen los cuatro archivos de 2025 con
`unionByName`; se muestran esquema y cinco registros; se contabilizan faltantes por
variable y archivo antes de filtrar. Los filtros tienen orden fijo y se reconcilian
los totales iniciales y finales. Se verifica la clave período–hogar–persona antes y
después de filtrar. Una huella de todas las columnas originales distingue repeticiones
exactas de conflictos, sin eliminar duplicados automáticamente.

Los descriptivos, cuantiles exactos, histogramas agregados, medianas por grupo y trimestre,
y correlaciones se calculan en Spark sobre todos los registros elegibles de 2025.
Pandas se usa para leer Excel y presentar agregaciones pequeñas. No se usa scikit-learn
ni se transfieren bases analíticas completas a pandas.

Los resultados no se ponderan por FACTOR y no son estimaciones oficiales poblacionales.
Se conserva el salario en quetzales, sin imputación ni recortes. El histograma logarítmico
sólo cambia la visualización. Las filas longitudinales no equivalen a personas distintas.
2026 se prepara y audita; su análisis salarial se reserva para la prueba final.

## Reproducción y trabajo grupal

`ejecutar_laboratorio.py` ejecuta de principio a fin y guarda las salidas en el notebook;
al completarse también genera HTML. `generar_notebook.py` reconstruye el notebook desde
sus fuentes, pero borra las salidas al regenerarlo: no es necesario ejecutarlo para
abrir o volver a correr el notebook.

El proyecto pertenece al repositorio Git `Data-Science`. Registrar las contribuciones
reales de cada integrante. Excel y derivados se excluyen de Git por tamaño; se conservan
las fuentes y el descargador para reproducibilidad.

Fuente: https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/
