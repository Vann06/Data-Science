# Laboratorio 4 — Parte 2 (ejercicios 1–3)

Este directorio contiene el avance ejecutable de preparación de datos,
construcción de la respuesta binaria y selección de predictores.

## Archivos principales

- `notebooks/data_prep.ipynb`: análisis, resultados, gráficas, decisiones y bibliografía.
- `src/preparar_ml.py`: pipeline reproducible que valida y procesa las 22 escenas.
- `outputs/`: figuras generadas por el notebook.
- `data/processed/`: dataset Parquet particionado y tablas auxiliares. Es un producto
  reproducible y está ignorado por Git.

## Ejecución

Desde la raíz del repositorio, con el entorno virtual activado:

```powershell
python l04_analisis_geoespacial/parte_2/src/preparar_ml.py `
  --project-dir l04_analisis_geoespacial
```

Después, abra `data_prep.ipynb` con el kernel del entorno virtual y ejecute todas
las celdas. El notebook reutiliza automáticamente los productos de la misma
versión del pipeline; si cambia la lógica de preparación, el script los regenera.

## Resultado verificado

- 22 escenas alineadas en EPSG:32615 y resolución de 10 m.
- 13,689,403 observaciones válidas.
- 0 % de valores faltantes después de la limpieza.
- Respuesta `alta_cyano` definida con el umbral OMS 2021 de 12 µg/L.
- 137,708 positivos (1.006 %) y razón de desbalance de 98.41:1.
- Conjunto predictor auditado para evitar bandas e índices usados directa o
  indirectamente en la construcción de la respuesta.
