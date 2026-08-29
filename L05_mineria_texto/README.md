# Laboratorio 5 — Mineria de textos y analisis de sentimiento

Este directorio contiene el desarrollo del Laboratorio 5: limpieza de los tuits del conjunto **Disaster Tweets**, analisis exploratorio, n-gramas, clasificacion y analisis de sentimiento.

## Contenido

- `data/raw/`: datos de entrada incluidos en el repositorio.
- `notebook/`: notebooks del flujo de trabajo.
- `src/`: funciones auxiliares de limpieza y analisis.
- `docs/Laboratorio_5_informe.md`: informe final fuente en Markdown.
- `docs/Laboratorio_5_informe.pdf`: informe final exportado a PDF.

## Requisitos e instalacion

Se recomienda Python 3.10 o superior y acceso a internet en la primera ejecucion, para descargar los recursos de NLTK. Desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Los recursos NLTK se descargan automaticamente en `data/nltk_data/` al ejecutar el notebook de limpieza. Esa carpeta, el entorno virtual y los CSV de `data/processed/` son artefactos regenerables y no se incluyen en Git.

## Orden de ejecucion

Inicie Jupyter desde `L05_mineria_texto`:

```powershell
jupyter notebook
```

Ejecute los notebooks completos en este orden:

1. `notebook/analisis_exploratorio.ipynb`
2. `notebook/limpieza.ipynb`
3. `notebook/analisis_post_limpieza.ipynb`
4. `notebook/modelado_y_sentimiento.ipynb`

El segundo notebook genera los datos limpios usados por los dos siguientes. En una clonacion nueva no es necesario copiar archivos `.pickle`: NLTK los reconstruye al correr la limpieza.

## Regenerar el informe

Tras ejecutar los notebooks, genere las figuras y el Markdown consolidado:

```powershell
python docs/generar_activos_informe.py
```

Luego exporte el PDF desde ese Markdown:

```powershell
python docs/exportar_markdown_pdf.py
```

El exportador utiliza Microsoft Edge/Chromium instalado en Windows y deja el archivo en `docs/Laboratorio_5_informe.pdf`, con el mismo tipo de salida que los informes de los laboratorios 3 y 4.

Como alternativa visual en VS Code, instale la extension **Markdown PDF** (`yzane.markdown-pdf`), abra `docs/Laboratorio_5_informe.md` y ejecute el comando **Markdown PDF: Export (pdf)** desde la paleta de comandos.

## Que se versiona

Se conservan los notebooks, codigo, datos crudos, figuras del informe, el Markdown y el PDF final. No se versionan los entornos virtuales, caches de Jupyter/Python, recursos descargados de NLTK ni datos procesados que pueden reconstruirse mediante los pasos anteriores.
