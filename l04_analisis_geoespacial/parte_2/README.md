# Laboratorio 4, Parte 2 (ejercicios 1–8)

Este directorio contiene el análisis ejecutable de preparación de datos,
construcción de la respuesta binaria, selección de predictores, entrenamiento,
validación (aleatoria, espacial y entre lagos) e interpretación de tres modelos
de clasificación.

## Archivos principales

- `notebooks/data_prep.ipynb`: ejercicios 1–3, integridad de fuentes, limpieza,
  construcción de la variable respuesta y selección de predictores.
- `notebooks/modelado_ml.ipynb`: ejercicios 4–7, entrenamiento y evaluación de
  Regresión Logística, Random Forest y XGBoost bajo validación aleatoria (5),
  validación espacial por bloques de 1 km (6) y generalización entre lagos (7).
  Reutiliza el mismo pipeline (`ejecutar_pipeline`/`ejecutar_modelos` con
  `reutilizar=True`) y puede ejecutarse de forma independiente porque repite la
  celda de preparación del entorno.
- `notebooks/interpretabilidad.ipynb`: ejercicio 8, carga el mejor modelo ya
  entrenado (`.joblib`, no reentrena) y lo explica: importancia global de
  variables, SHAP summary plot y dependence plots, con interpretación ambiental.
- `src/preparar_ml.py`: pipeline reproducible que valida y procesa las 22 escenas.
- `src/modelar_ml.py`: muestreo reproducible, división 70/30, ajuste y evaluación
  de Regresión Logística, Random Forest y XGBoost.
- `outputs/`: figuras generadas por el notebook.
- `data/processed/`: dataset Parquet particionado y tablas auxiliares. Es un producto
  reproducible y está ignorado por Git.

## Ejecución

**Prerrequisito:** `preparar_ml.py` necesita un GeoTIFF de 9 bandas por escena en
`data/<lago>/<fecha>_bandas.tif` (carpetas ignoradas por Git, cada quien las genera
localmente). Si no las tiene todavía, descárguelas primero:

```powershell
python l04_analisis_geoespacial/src/descargar_bandas.py
```

Requiere una cuenta de Copernicus Data Space (login interactivo vía openEO) y puede
tardar bastante en las 22 escenas; si el archivo de una escena ya existe, se omite.

Después, desde la raíz del repositorio, con el entorno virtual activado:

```powershell
python l04_analisis_geoespacial/parte_2/src/preparar_ml.py `
  --project-dir l04_analisis_geoespacial

python l04_analisis_geoespacial/parte_2/src/modelar_ml.py `
  --project-dir l04_analisis_geoespacial
```

Después, abra `data_prep.ipynb` con el kernel del entorno virtual y ejecute todas
las celdas para ver la preparación de datos (ejercicios 1–3); luego abra
`modelado_ml.ipynb` para el entrenamiento y las tres validaciones (ejercicios
4–7). Ambos notebooks reutilizan automáticamente los productos de la misma versión
del pipeline; si cambia la lógica de preparación, se regeneran.

Finalmente, `interpretabilidad.ipynb` (ejercicio 8) requiere `shap` (incluido en
`requirements.txt`) y los `.joblib` de `data/processed/modelos/estimadores/`, que
genera `modelado_ml.ipynb` al correr `ejecutar_modelos`.

## Resultado verificado

- 22 escenas alineadas en EPSG:32615 y resolución de 10 m.
- 13,689,403 observaciones válidas.
- 0 % de valores faltantes después de la limpieza.
- Respuesta `alta_cyano` definida con el umbral OMS 2021 de 12 µg/L.
- 137,708 positivos (1.006 %) y razón de desbalance de 98.41:1.
- Conjunto predictor auditado para evitar bandas e índices usados directa o
  indirectamente en la construcción de la respuesta.
- Muestra proporcional y reproducible de 600,000 observaciones: 420,000 para
  entrenamiento y 180,000 para una prueba común a los tres modelos.
- Ajuste de hiperparámetros realizado exclusivamente con una partición interna
  del entrenamiento; el conjunto de prueba no interviene en la selección.
- **Validación aleatoria (70/30):** Random Forest da el mejor resultado nominal
  (PR-AUC 0.967, recall 0.975, F2 0.935 con el umbral operativo), seguido de
  XGBoost (PR-AUC 0.959) y Regresión Logística (PR-AUC 0.821).
- **Validación espacial (`StratifiedGroupKFold` por bloques de 1 km, sección 6):**
  el desempeño de los tres modelos cae frente a la validación aleatoria, pero de
  forma muy desigual: Random Forest es el más afectado (PR-AUC 0.967 → 0.872,
  recall 0.975 → 0.832), XGBoost cae menos (PR-AUC 0.959 → 0.901, recall 0.977 →
  0.916) y Regresión Logística casi no se mueve (PR-AUC 0.821 → 0.803). **XGBoost
  queda como el modelo más robusto y se adopta como el modelo final**, no Random
  Forest, porque su desempeño depende menos de la autocorrelación espacial entre
  píxeles de entrenamiento y prueba.
- **Generalización entre lagos (sección 7):** ningún modelo entrenado en un lago
  generaliza adecuadamente al otro. Entrenar en Atitlán y evaluar en Amatitlán
  falla por escasez de positivos de entrenamiento (solo 136, recall de Random
  Forest cae a 2.4 %); entrenar en Amatitlán y evaluar en Atitlán da recall
  razonable pero precisión inutilizable (0.7–11.7 %) por la rareza real de la
  floración en Atitlán (~0.03 % frente a ~9 % en Amatitlán).
- **Interpretabilidad (SHAP, sección 8):** la variable más influyente sobre las
  predicciones de XGBoost es `b07` (relación no lineal saturante: a mayor
  reflectancia, mayor probabilidad de presencia elevada), seguida de las
  coordenadas `x_utm`/`y_utm`. La fuerte dependencia en la ubicación geográfica
  explica, en parte, por qué el modelo no generaliza bien entre lagos.
- Evaluación desagregada por lago y advertencia explícita sobre autocorrelación
  espacial y la escasez de positivos de Atitlán en la muestra de prueba.
