# Laboratorio 2 — Deep Learning y Catch22

## Objetivo

Aplicar modelos LSTM a las series temporales construidas en el Laboratorio 1
y analizar sus similitudes mediante las 22 características de Catch22.

## Series utilizadas

1. Total internacional.
2. Aérea.
3. Terrestre.
4. Marítima.
5. América del Centro.
6. América del Norte.
7. Europa.

Todas las series cubren el período de enero de 2009 a junio de 2026.

## Estructura

```text
L02_DL_series/
├── data/
├── docs/
├── img/
├── notebooks/
├── src/
└── README.md
```

## Orden de los notebooks

| Notebook | Descripción |
|---|---|
| `01_lstm_series_geograficas.ipynb` | Modelos LSTM para las series geográficas |
| `02_lstm_serie_total.ipynb` | Modelo LSTM para la serie total internacional |
| `03_extraccion_catch22.ipynb` | Construcción de las siete series y extracción de Catch22 |
| `04_agrupamiento_series.ipynb` | PCA, clustering, heatmap, correlaciones y distancias |
| `05_lstm_catch22.ipynb` | Modelo LSTM adicional con características Catch22 |

## Carpetas

- `data/`: archivos CSV generados durante el Laboratorio 2.
- `docs/`: informes, explicaciones y conclusiones.
- `img/`: gráficas utilizadas en los informes.
- `notebooks/`: desarrollo ordenado del análisis.
- `src/`: funciones compartidas para cargar datos, construir series,
  calcular Catch22 y evaluar modelos.

## Archivos generados

El notebook `03_extraccion_catch22.ipynb` debe producir:

```text
data/series_mensuales.csv
data/catch22_features.csv
data/catch22_features_scaled.csv
```

Estos archivos serán utilizados por los notebooks posteriores.

## Flujo de trabajo

1. Cargar la base original desde `data/raw/`.
2. Construir las siete series mensuales.
3. Verificar fechas, longitud y valores faltantes.
4. Extraer las 22 características Catch22.
5. Estandarizar la matriz de características.
6. Realizar PCA, clustering y análisis de similitud.
7. Comparar los modelos LSTM.
8. Integrar los resultados en el informe final.

## Reglas del equipo

1. No modificar el archivo Excel original.
2. No repetir la construcción completa de las series en cada notebook.
3. Utilizar las funciones disponibles en `src/`.
4. Ejecutar cada notebook desde cero antes de integrarlo.
5. Mantener el orden numérico de los notebooks.
6. No utilizar el conjunto de prueba para seleccionar hiperparámetros.
7. Documentar brevemente las decisiones y los resultados.
8. Probar primero los cambios en `lab2_test` antes de integrarlos a `Lab2`.

## Instalación

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\activate
```

Después:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook
```
