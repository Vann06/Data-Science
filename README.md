# Data Science · CC3084

Repositorio académico para los ejercicios, laboratorios y proyectos del curso **CC3084 · Data Science** de la Universidad del Valle de Guatemala.

El objetivo es mantener cada trabajo organizado, documentado y reproducible, incluyendo datos, cuadernos de análisis, dependencias, resultados y conclusiones.

## Sitio publicado

Los cuadernos se presentan también como un sitio creado con **Quarto** y publicado mediante **GitHub Pages**:

**https://vann06.github.io/Data-Science/**

Los cambios enviados a `main` activan el proceso definido en `.github/workflows/publish.yml`.

## Proyectos

| Proyecto | Descripción | Herramientas |
|---|---|---|
| Laboratorio 1 · Series de tiempo | Análisis exploratorio y modelos clásicos de pronóstico. | Python, pandas, statsmodels, scikit-learn, Matplotlib |
| **Laboratorio 2 · Deep Learning** | Modelos LSTM, tuneo de hiperparámetros, comparación con el Laboratorio 1 y análisis de similitud mediante catch22. | Python, TensorFlow/Keras, pycatch22, scikit-learn |

---

# Laboratorio 2 · Deep Learning para Series de Tiempo

> Rama de trabajo: `Lab2`  
> Entrega final: **2 de agosto de 2026, 23:59**

## Objetivos del laboratorio

1. Utilizar los mismos conjuntos de entrenamiento y prueba del Laboratorio 1.
2. Trabajar con al menos dos series temporales.
3. Crear al menos dos configuraciones LSTM diferentes por cada serie seleccionada.
4. Hacer tuneo de hiperparámetros y seleccionar el mejor modelo.
5. Predecir con el mejor LSTM y compararlo con el mejor modelo del Laboratorio 1.
6. Extraer las 22 características de catch22 para todas las series construidas anteriormente.
7. Estandarizar las características y realizar PCA, clustering, heatmaps, correlaciones y análisis de distancias.
8. Crear un modelo LSTM adicional con características de catch22 y compararlo con el mejor LSTM tradicional.

## Estructura de trabajo actual

```text
Data-Science/
├── README.md
└── L01_series_tiempo/
    ├── data/
    │   ├── raw/                         # Datos originales; no modificar
    │   └── processed/                   # Resultados y datos derivados
    ├── notebooks/
    │   ├── vias_de_ingreso.ipynb
    │   ├── laboratorio2_Geograficas.ipynb
    │   └── seire_total_internacional_LSTM.ipynb
    ├── scripts/                         # Funciones reutilizables
    ├── figures/                         # Gráficas finales
    └── reports/                         # Informe y entregables
```

Los nombres anteriores corresponden a los archivos existentes en la rama `Lab2`. No se deben renombrar durante el desarrollo sin coordinarlo con todo el equipo.

## División justa para tres integrantes

| Responsable | Archivo principal | Entregables individuales |
|---|---|---|
| **Integrante 1 · Vías de ingreso** | `L01_series_tiempo/notebooks/vias_de_ingreso.ipynb` | Desarrollar una serie viable de vía de ingreso con al menos dos configuraciones LSTM, tuneo, selección del mejor modelo, predicción y comparación con el Laboratorio 1. Extraer también catch22 para todas las series de vías y redactar sus hallazgos. La serie marítima no se usará para el LSTM porque no contiene observaciones posteriores a 2017; esta limitación debe quedar documentada. |
| **Integrante 2 · Series geográficas** | `L01_series_tiempo/notebooks/laboratorio2_Geograficas.ipynb` | Desarrollar la segunda serie requerida con al menos dos configuraciones LSTM, tuneo, selección, predicción y comparación con el Laboratorio 1. Extraer catch22 para todas las series geográficas y redactar sus hallazgos locales. |
| **Integrante 3 · Serie total e integración** | `L01_series_tiempo/notebooks/seire_total_internacional_LSTM.ipynb` | Extraer catch22 para la serie total, unir los resultados de los otros integrantes, estandarizar la matriz y realizar PCA, clustering, heatmaps, correlaciones y distancias. Construir el LSTM con variables de catch22 y consolidar las conclusiones globales. |

Esta distribución deja a los integrantes 1 y 2 con una serie LSTM completa cada uno. El integrante 3 asume la integración estadística, las visualizaciones globales y el modelo adicional con catch22.

## Contrato común para integrar resultados

Cada integrante debe conservar el nombre original de sus series y producir las métricas LSTM con una estructura común:

```text
serie, modelo, ventana, unidades, dropout, learning_rate, batch_size,
epochs, MAE, RMSE, MAPE_o_sMAPE
```

Los resultados de catch22 deben cumplir lo siguiente:

- Una fila por serie temporal.
- Una columna identificadora llamada `serie`.
- Las 22 características en columnas separadas.
- Valores sin estandarizar en los archivos individuales.
- La estandarización debe realizarse una sola vez sobre la matriz completa.

Archivos sugeridos:

```text
L01_series_tiempo/data/processed/
├── metricas_lstm_vias.csv
├── metricas_lstm_geograficas.csv
├── catch22_vias.csv
├── catch22_geograficas.csv
├── catch22_total.csv
└── catch22_matriz_completa.csv
```

## Estructura mínima de cada notebook LSTM

1. Objetivo y justificación de la serie seleccionada.
2. Carga y validación de datos.
3. Reutilización exacta del corte de entrenamiento y prueba del Laboratorio 1.
4. Escalado ajustado solamente con entrenamiento.
5. Construcción de ventanas temporales.
6. Primera configuración LSTM.
7. Segunda configuración LSTM.
8. Tuneo de hiperparámetros.
9. Selección del mejor modelo usando validación.
10. Predicción sobre prueba.
11. Inversión del escalado y métricas en la escala original.
12. Comparación con el mejor modelo del Laboratorio 1 usando el mismo horizonte y las mismas métricas.
13. Interpretación, limitaciones y conclusión.

## Estructura mínima del análisis catch22

1. Explicación breve de la idea detrás de catch22.
2. Extracción de las 22 características para todas las series.
3. Construcción de la matriz completa.
4. Estandarización.
5. PCA.
6. Clustering.
7. Heatmap de características.
8. Matriz de correlaciones.
9. Mapa de distancias entre series.
10. Identificación de similitudes, grupos naturales y series atípicas.
11. Comparación con tendencia, estacionalidad, volatilidad, pandemia y autocorrelación observadas en el Laboratorio 1.
12. Tres descubrimientos nuevos obtenidos mediante catch22.
13. Modelo LSTM con variables de catch22 y comparación final.

## Plan para cerrar hoy la parte de Vías de ingreso

La persona responsable de `vias_de_ingreso.ipynb` puede terminar su bloque sin esperar la integración global:

- [ ] Seleccionar la serie aérea o terrestre para el LSTM; no usar marítima como serie principal.
- [ ] Confirmar que el train/test sea exactamente el del Laboratorio 1.
- [ ] Recuperar las métricas del mejor modelo anterior.
- [ ] Entrenar dos configuraciones LSTM claramente diferentes.
- [ ] Hacer un tuneo pequeño y reproducible.
- [ ] Elegir el mejor modelo con validación, no con el conjunto de prueba.
- [ ] Generar predicciones y métricas en escala original.
- [ ] Comparar contra el modelo anterior usando el mismo período de prueba.
- [ ] Extraer catch22 para todas las series de vías disponibles.
- [ ] Exportar `metricas_lstm_vias.csv` y `catch22_vias.csv`.
- [ ] Escribir conclusiones breves dentro del notebook.
- [ ] Hacer commits propios y abrir un Pull Request hacia `Lab2`.

## Flujo de trabajo en GitHub

1. Crear una rama individual desde `Lab2`:
   - `lab2-vias-<nombre>`
   - `lab2-geograficas-<nombre>`
   - `lab2-integracion-<nombre>`
2. No modificar archivos de otra persona sin coordinación.
3. No alterar archivos de `data/raw/`.
4. Hacer commits pequeños y descriptivos.
5. Guardar gráficas finales en `figures/` y resultados tabulares en `data/processed/`.
6. Abrir un Pull Request hacia `Lab2`.
7. Resolver conflictos antes de integrar.
8. Conservar el historial individual, porque la evaluación considera las contribuciones de cada integrante.

Ejemplos de commits:

```text
feat: agregar primer modelo LSTM para via aerea
feat: tunear hiperparametros del LSTM de vias
analysis: comparar LSTM con modelo del laboratorio 1
data: exportar caracteristicas catch22 de vias
report: documentar resultados y limitaciones de vias
```

## Lista final de verificación

- [ ] Dos series seleccionadas con el mismo train/test del Laboratorio 1.
- [ ] Dos o más configuraciones LSTM por serie.
- [ ] Tuneo documentado.
- [ ] Mejor modelo elegido con un criterio explícito.
- [ ] Predicciones y gráficas en escala original.
- [ ] Comparación contra los modelos del Laboratorio 1.
- [ ] catch22 aplicado a todas las series.
- [ ] Matriz completa y estandarizada.
- [ ] PCA, clustering, heatmaps, correlaciones y distancias.
- [ ] Respuestas interpretativas completas.
- [ ] LSTM adicional con características de catch22.
- [ ] Código reproducible y contribuciones versionadas.
- [ ] Informe o notebooks con todas las explicaciones.

## Tecnologías utilizadas

- Python y Jupyter Notebook.
- pandas y NumPy para manipulación de datos.
- TensorFlow/Keras para modelos LSTM.
- scikit-learn para preprocesamiento, métricas, PCA y clustering.
- pycatch22 para extracción de características.
- Matplotlib para visualizaciones.
- Quarto, GitHub Actions y GitHub Pages para publicación.

## Ejecución local

```bash
git clone https://github.com/Vann06/Data-Science.git
cd Data-Science
git checkout Lab2
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\activate
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Después, instalar las dependencias del proyecto y abrir Jupyter Notebook.

---

Repositorio desarrollado como área de trabajo académica para **CC3084 · Data Science, Universidad del Valle de Guatemala**.
