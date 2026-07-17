# Series de tiempo - temperatura de Guatemala

Este proyecto resuelve la hoja de ejercicios 1 al 8 con Python.

## Cómo ejecutarlo en Windows

```powershell
cd Data-Science
python -m venv .venv
.venv\Scripts\activate
pip install -r 01_series_tiempo/requirements.txt
jupyter notebook 01_series_tiempo/notebooks/series-tiempo.ipynb
```

En Jupyter, abra `series-tiempo.ipynb` y ejecute la única celda. Esa celda llama al script completo `src/series_tiempo.py`.

## Qué incluye

- exploración y extremos de todas las capas;
- división entrenamiento/prueba con los últimos 36 meses;
- descomposición, tendencia y estacionariedad;
- ACF y PACF;
- tres modelos SARIMA;
- validación de coeficientes, raíces, residuos, AIC y BIC;
- pronóstico del conjunto de prueba;
- comparación con Holt-Winters, suavizamiento exponencial y naive estacional;
- pronóstico de 12 meses posteriores a junio de 2026.

## Archivos

- `data/raw/guatemala_temperatura.csv`: datos originales.
- `notebooks/series-tiempo.ipynb`: punto de entrada para Jupyter.
- `src/series_tiempo.py`: solución completa.
- `codebook.md`: descripción de variables.
