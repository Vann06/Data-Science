# CC3084 · Data Science

Repositorio académico del curso **CC3084 · Data Science** de la Universidad del Valle de Guatemala.

La rama actual de trabajo es **`Lab2`** y contiene el Laboratorio 1 de series de tiempo junto con los avances del **Laboratorio 2: Deep Learning**.

> **Entrega final:** 2 de agosto de 2026 a las 23:59.

## Objetivo del Laboratorio 2

El laboratorio solicita:

1. Utilizar los mismos conjuntos de entrenamiento y prueba del Laboratorio 1.
2. Trabajar con al menos dos series temporales.
3. Probar al menos dos configuraciones LSTM por serie y realizar tuneo de parámetros.
4. Seleccionar el mejor modelo, generar predicciones y compararlo con el mejor modelo del Laboratorio 1.
5. Extraer las 22 características de catch22 para todas las series construidas anteriormente.
6. Estandarizar la matriz de características y realizar PCA, clustering, heatmap, correlaciones y análisis de distancias.
7. Interpretar las similitudes, grupos, características importantes y series atípicas.
8. Construir un LSTM adicional con características de catch22 y compararlo con el mejor LSTM convencional.

## Estado real del repositorio

| Bloque | Estado | Evidencia principal |
|---|---|---|
| Laboratorio 1: análisis exploratorio y modelos clásicos | Completado | `L01_series_tiempo/informe_series_de_tiempo.md` |
| Ejercicio 1 del Laboratorio 2 | **Avance sustancialmente completado** | `L01_series_tiempo/notebooks/laboratorio2_Geograficas.ipynb` |
| LSTM adicional de la serie total internacional | Desarrollado | `L01_series_tiempo/notebooks/seire_total_internacional_LSTM.ipynb` |
| Series por vías de ingreso | Construidas en el Laboratorio 1 | `L01_series_tiempo/notebooks/vias_de_ingreso.ipynb` |
| Ejercicio 2: catch22 y análisis de similitud | **Pendiente** | No se encontró todavía una implementación integrada |
| Informe final del Laboratorio 2 | **Pendiente** | El informe existente corresponde al Laboratorio 1 |

### Aclaración importante

El notebook `laboratorio2_Geograficas.ipynb` ya trabaja con **dos series** —América del Centro y Europa—, prueba varias configuraciones LSTM, realiza selección mediante validación, genera predicciones y compara con modelos del Laboratorio 1.

Por lo tanto, **no es obligatorio construir otro LSTM para vías de ingreso** para cumplir el mínimo de dos series. Las series de vías sí deben incluirse en catch22 porque el ejercicio solicita utilizar todas las series construidas anteriormente.

## Qué falta para terminar

### Ejercicio 1 — Revisión final

- [ ] Ejecutar `laboratorio2_Geograficas.ipynb` desde cero y confirmar que todas las celdas funcionen en orden.
- [ ] Verificar que las comparaciones utilicen exactamente el mismo período de prueba del Laboratorio 1.
- [ ] Confirmar que las conclusiones respondan claramente cuál serie fue mejor predicha y si LSTM superó o no al modelo anterior.
- [ ] Consolidar la tabla final de métricas para que pueda incorporarse al informe.

### Ejercicio 2 — Pendiente principal

- [ ] Explicar brevemente la idea e importancia de catch22.
- [ ] Extraer las 22 características para la serie total y todas las series geográficas y de vías de ingreso.
- [ ] Construir una matriz con una fila por serie y una columna por característica.
- [ ] Estandarizar las características.
- [ ] Realizar PCA.
- [ ] Realizar clustering.
- [ ] Crear el heatmap de características.
- [ ] Crear la matriz de correlaciones entre características.
- [ ] Crear el mapa de distancias entre series.
- [ ] Responder los incisos de interpretación 2.7–2.13.
- [ ] Construir el LSTM con características catch22 del inciso 2.14.
- [ ] Compararlo con el mejor LSTM convencional y discutir los resultados.

### Entrega y reproducibilidad

- [ ] Integrar los resultados del Laboratorio 2 en un informe o notebook final.
- [ ] Actualizar `requirements.txt` con todas las librerías realmente utilizadas, incluyendo las necesarias para catch22 y tuneo.
- [ ] Eliminar errores o advertencias que afecten la lectura de los resultados.
- [ ] Dejar evidencia de las contribuciones individuales mediante commits.
- [ ] Incluir el enlace de Google Drive y el enlace del repositorio en la entrega.

## División justa para tres integrantes

La siguiente distribución evita repetir el Ejercicio 1, permite trabajar en paralelo y deja una contribución técnica verificable para cada persona.

| Integrante | Responsabilidad | Entregable |
|---|---|---|
| **Integrante 1 — Extracción catch22** | Crear una función reutilizable para extraer las 22 características, aplicarla a todas las series, construir la matriz y generar su versión estandarizada. | Código reproducible, matriz sin escalar, matriz estandarizada y explicación del inciso 2.1. |
| **Integrante 2 — Exploración de similitud** | Trabajar con la matriz estandarizada y realizar PCA, clustering, heatmap, correlaciones y mapa de distancias. Responder 2.7–2.10. | Cinco análisis gráficos, criterios metodológicos y primeras interpretaciones. |
| **Integrante 3 — Interpretación y modelo final** | Responder 2.11–2.13, construir el LSTM con características catch22 del inciso 2.14, comparar resultados e integrar las conclusiones finales. | Interpretación completa, nuevo modelo, tabla comparativa y conclusiones. |

### Parte recomendada para terminar hoy

La parte del **Integrante 1** puede cerrarse hoy sin esperar a los demás:

1. Identificar todas las series ya creadas en los notebooks del Laboratorio 1.
2. Convertir cada serie a un arreglo numérico limpio y ordenado cronológicamente.
3. Extraer las 22 características de catch22 con una sola función.
4. Crear una tabla con `serie` como identificador y 22 columnas de características.
5. Revisar valores faltantes o infinitos.
6. Estandarizar únicamente las columnas numéricas.
7. Guardar ambas matrices y documentar qué series fueron incluidas.
8. Hacer commits propios con mensajes claros.

Con este bloque terminado, los otros dos integrantes pueden trabajar directamente sobre la misma matriz sin modificar el código de extracción.

## Estructura actual

```text
Data-Science/
├── L01_series_tiempo/
│   ├── data/
│   │   ├── Base_Migracion_2009-2026jun.csv.xlsx
│   │   └── raw/
│   │       └── Base_Migracion_2009-2026jun.xlsx
│   ├── notebooks/
│   │   ├── Analisis_zonas_geograficas.ipynb
│   │   ├── analisis_exploratorio.ipynb
│   │   ├── analisis_preliminar_series.ipynb
│   │   ├── analisis_serie_total_internacional.ipynb
│   │   ├── laboratorio2_Geograficas.ipynb
│   │   ├── seire_total_internacional_LSTM.ipynb
│   │   └── vias_de_ingreso.ipynb
│   ├── codebook.md
│   ├── informe_series_de_tiempo.md
│   ├── informe_series_de_tiempo.pdf
│   └── README.md
├── .github/workflows/
│   └── publish.yml
├── _quarto.yml
├── index.qmd
├── requirements.txt
├── styles.css
└── README.md
```

## Flujo de trabajo recomendado

Cada integrante debe trabajar desde `Lab2` en una rama propia:

```text
lab2-catch22-extraccion-<nombre>
lab2-catch22-analisis-<nombre>
lab2-catch22-modelo-<nombre>
```

Reglas de integración:

- No modificar los datos originales.
- No seleccionar hiperparámetros usando el conjunto de prueba.
- No estandarizar cada grupo por separado; la matriz completa debe estandarizarse una sola vez.
- Mantener una fila por serie y las mismas 22 columnas para todos.
- Ejecutar el notebook completo antes de abrir el Pull Request.
- Hacer commits pequeños y descriptivos.
- Conservar el historial individual porque la calificación considera las contribuciones de cada integrante.

Ejemplos de commits:

```text
feat: extraer caracteristicas catch22 de todas las series
feat: construir matriz estandarizada de catch22
analysis: agregar PCA y clustering de series
analysis: interpretar series atipicas y grupos naturales
model: comparar LSTM con variables catch22
report: integrar conclusiones del laboratorio 2
```

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

Después:

```bash
pip install -r requirements.txt
jupyter notebook
```

## Publicación

El sitio del curso se publica mediante Quarto y GitHub Pages:

**https://vann06.github.io/Data-Science/**

La publicación automática se encuentra configurada en `.github/workflows/publish.yml`.
