# CC3084 — Data Science

Repositorio del curso **CC3084 Data Science**.

El proyecto analiza series mensuales de viajeros internacionales que ingresan
a Guatemala entre enero de 2009 y junio de 2026.

## Laboratorios

- `L01_series_tiempo/`: análisis exploratorio, construcción de series y
  modelos clásicos de series de tiempo.
- `L02_DL_series/`: modelos LSTM, extracción de características Catch22,
  agrupamiento y comparación de resultados.

## Datos

El archivo original se encuentra en:

`data/raw/Base_Migracion_2009-2026jun.xlsx`

El archivo original no debe modificarse. Los resultados generados por el
Laboratorio 2 se guardan dentro de `L02_DL_series/data/`.

## Estructura

```text
Data-Science/
├── data/
│   └── raw/
├── L01_series_tiempo/
├── L02_DL_series/
├── requirements.txt
└── README.md
```

## Instalación

Crear el entorno virtual:

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\activate
```

Instalar las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Abrir los notebooks:

```bash
jupyter notebook
```

