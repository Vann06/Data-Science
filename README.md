# Data Science · CC3084

Repositorio académico de trabajo para los ejercicios, laboratorios y proyectos desarrollados durante el curso **CC3084 · Data Science**.

El objetivo es mantener cada proyecto organizado, documentado y reproducible, incluyendo el conjunto de datos, el cuaderno de análisis, las dependencias y las conclusiones principales.

## Sitio publicado

Los cuadernos se presentan también como un sitio web creado con **Quarto** y publicado automáticamente mediante **GitHub Pages**:

**https://vann06.github.io/Data-Science/**

Cada cambio enviado a la rama `main` activa el proceso de publicación definido en `.github/workflows/publish.yml`.
## Proyectos

| Proyecto | Descripción | Herramientas |
|---|---|---|
| [01 · Series de tiempo](01_series_tiempo/) | Análisis y predicción de la temperatura promedio mensual de Guatemala entre 1950 y 2026.<br><br>Incluye estacionariedad, ARIMA/SARIMA, Holt-Winters, suavizamiento exponencial y naive estacional. | Python, pandas, statsmodels, scikit-learn, Matplotlib |


## Estructura del repositorio

```text
Data-Science/
├── 01_series_tiempo/
│   ├── data/
│   │   └── raw/                  # Datos originales
│   ├── notebooks/                # Cuadernos de análisis
│   ├── codebook.md               # Descripción de variables
│   ├── README.md                 # Documentación del proyecto
│   └── requirements.txt          # Dependencias del proyecto
├── .github/workflows/
│   └── publish.yml               # Publicación automática en GitHub Pages
├── _quarto.yml                   # Configuración del sitio
├── index.qmd                     # Página de inicio
├── styles.css                    # Estilos visuales del sitio
└── README.md
```

## Tecnologías utilizadas

- **Python** para el análisis y modelado.
- **Jupyter Notebook** para combinar código, resultados, gráficas y explicaciones.
- **pandas y NumPy** para manipulación de datos.
- **Matplotlib** para visualización.
- **SciPy y statsmodels** para pruebas estadísticas y modelos de series de tiempo.
- **scikit-learn** para métricas de evaluación.
- **Quarto** para convertir los cuadernos en un sitio web.
- **GitHub Actions y GitHub Pages** para publicación automática.

## Cómo ejecutar un proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/Vann06/Data-Science.git
cd Data-Science
```

### 2. Crear y activar un entorno virtual

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias del proyecto

```bash
pip install -r 01_series_tiempo/requirements.txt
```

### 4. Abrir el cuaderno

```bash
jupyter notebook 01_series_tiempo/notebooks/series-tiempo.ipynb
```

## Convenciones de trabajo

Cada proyecto se mantiene en una carpeta independiente y debe contener:

1. Los datos originales sin modificar en `data/raw/`.
2. Uno o más cuadernos en `notebooks/`.
3. Un archivo `requirements.txt` con las dependencias.
4. Un `README.md` con el objetivo, metodología y forma de ejecución.
5. Un `codebook.md` cuando el conjunto de datos requiera explicación de variables.
6. Resultados y conclusiones escritos de forma clara y respaldados por el análisis.


Repositorio desarrollado como área de trabajo académica para el curso **CC3084 · Data Science, Universidad del Valle de Guatemala**.
