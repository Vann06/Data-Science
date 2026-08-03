 Informe de extracción de características de series de tiempo (Catch22)

## 1. Objetivo

Representar las siete series temporales construidas en el Laboratorio 1 mediante un conjunto común y comparable de características. Para ello se calculan exactamente las 22 características de **catch22** para cada serie y después se estandariza la matriz resultante.

- explicar la idea e importancia de catch22;
- extraer las 22 características para todas las series;
- construir una matriz con una fila por serie y una columna por característica;
- estandarizar las características antes de cualquier comparación.

## 2. Pregunta de análisis

**¿Cómo puede resumirse el comportamiento dinámico de las siete series temporales mediante una representación común que permita compararlas posteriormente con PCA, clustering, correlaciones y distancias?**

## 3. Series utilizadas

Se utilizaron todas las series construidas en el Laboratorio 1:

| Serie | Definición utilizada |
|---|---|
| `total_internacional` | Turistas y excursionistas, excluyendo los registros cuyo país es Guatemala |
| `aerea` | Turistas y excursionistas que ingresaron por vía aérea |
| `terrestre` | Turistas y excursionistas que ingresaron por vía terrestre |
| `maritima` | Ingresos por vía marítima, conservando todos los tipos de viajero según la decisión metodológica del Laboratorio 1 |
| `america_centro` | Turistas y excursionistas clasificados en América del Centro |
| `america_norte` | Turistas y excursionistas clasificados en América del Norte |
| `europa` | Turistas y excursionistas clasificados en Europa |

Cada serie contiene **210 observaciones mensuales**, desde enero de 2009 hasta junio de 2026.

## 4. Preparación y validación de las series

Antes de extraer características se verificó que:

- las siete series utilizaran el mismo calendario mensual;
- las fechas estuvieran ordenadas y sin duplicados;
- no existieran valores faltantes, infinitos ni negativos;
- ninguna serie fuera constante;
- todas las series conservaran exactamente 210 observaciones.

La matriz de series se almacenó en `L02_DL_series/data/series_mensuales.csv`. Las fechas ocupan las filas y las siete series ocupan las columnas. Este formato ancho facilita comprobar que todas las series comparten el mismo calendario.

## 5. ¿Qué es Catch22 y por qué es importante? — Inciso 2.1

Catch22 significa **22 CAnonical Time-series CHaracteristics**. Su idea principal es transformar una serie temporal completa en un vector corto de 22 medidas que resumen distintos aspectos de su comportamiento dinámico. Las características incluyen información relacionada con la distribución de valores, autocorrelación lineal y no lineal, predictibilidad, cambios sucesivos, presencia de valores atípicos, periodicidad y escalamiento de las fluctuaciones.

El conjunto fue seleccionado a partir de una biblioteca mucho más grande de características de series de tiempo. El objetivo fue conservar medidas informativas y poco redundantes, pero con un costo computacional mucho menor. Esto es importante porque permite expresar series con escalas y patrones diferentes en un mismo espacio de características y, posteriormente, compararlas mediante técnicas como PCA, clustering o distancias.

En este laboratorio se utilizó `catch24=False`, por lo que se calcularon exactamente las 22 características solicitadas. No se agregaron la media y la desviación estándar que formarían el conjunto opcional catch24.

## 6. Extracción de características — Inciso 2.2

Para cada una de las siete series se ejecutó `pycatch22.catch22_all(..., catch24=False)`. Se comprobó que cada ejecución devolviera exactamente 22 nombres y 22 valores.

También se verificó que todos los resultados fueran finitos. Una serie constante o incorrectamente filtrada puede producir características indefinidas; por eso la validación de las series se realizó antes de la extracción.

## 7. Construcción de la matriz — Inciso 2.3

La matriz sin escalar se guardó en:

`L02_DL_series/data/catch22_features.csv`

Su estructura es:

- **7 filas:** una por cada serie temporal;
- **22 columnas:** una por cada característica catch22;
- **índice:** nombre de la serie.

La dimensión esperada y validada es:

`(7, 22)`

Este es el archivo principal que demuestra el cumplimiento del inciso 2.3.

## 8. Estandarización — Inciso 2.4

Las características catch22 tienen unidades y rangos diferentes. Compararlas directamente podría provocar que las características con magnitudes numéricas mayores dominaran métodos basados en varianza o distancia.

Por ello se utilizó `StandardScaler` sobre la matriz completa. Para cada característica se aplicó:

\[
z = \frac{x - \mu}{\sigma}
\]

donde \(\mu\) es la media de esa característica entre las siete series y \(\sigma\) es su desviación estándar poblacional.

La matriz estandarizada se guardó en:

`L02_DL_series/data/catch22_features_scaled.csv`

La estandarización se hizo **una sola vez sobre la matriz completa**, no por serie ni por grupo. La matriz escalada conserva exactamente los mismos nombres de filas y columnas que la matriz original.

## 9. Archivos generados

| Archivo | Dimensión | Uso |
|---|---:|---|
| `series_mensuales.csv` | 210 × 7 | Auditoría y reproducción de las siete series |
| `catch22_features.csv` | 7 × 22 | Matriz original de características |
| `catch22_features_scaled.csv` | 7 × 22 | Entrada para análisis comparativos posteriores |

No se separaron las series en siete CSV distintos porque un único archivo ancho mantiene todas las fechas alineadas, reduce duplicación y facilita la validación. Si más adelante un modelo necesita una serie individual, puede seleccionarse directamente una columna de `series_mensuales.csv`.

## 10. Pruebas de validez

El script `validar_catch22_outputs.py` verifica de forma independiente que:

1. los tres archivos existan;
2. la matriz de series sea 210 × 7;
3. las fechas cubran exactamente enero de 2009 a junio de 2026;
4. no existan faltantes, infinitos, negativos ni series constantes;
5. los acumulados coincidan con los filtros aplicados al Excel original;
6. la matriz catch22 sea 7 × 22;
7. una extracción nueva de catch22 coincida con el CSV guardado;
8. la matriz estandarizada coincida con `StandardScaler`;
9. cada característica estandarizada tenga media aproximada cero y desviación poblacional aproximada uno, salvo una eventual característica constante.

## 11. Conclusiones

Se completó una representación común de las siete series temporales mediante las 22 características de catch22. La matriz resultante cumple la estructura solicitada: una fila por serie y una columna por característica.

La versión estandarizada deja los datos preparados para los análisis posteriores de componentes principales, agrupamiento, heatmaps, correlaciones y distancias. La separación entre matriz original y matriz escalada permite conservar los valores calculados por catch22 y, al mismo tiempo, disponer de una entrada adecuada para métodos comparativos.

## 12. Referencias

- Lubba, C. H., Sethi, S. S., Knaute, P., Schultz, S. R., Fulcher, B. D. y Jones, N. S. (2019). *catch22: CAnonical Time-series CHaracteristics*. Data Mining and Knowledge Discovery, 33, 1821–1852. https://doi.org/10.1007/s10618-019-00647-x
- pycatch22. *22 CAnonical Time-series Features in Python*. https://pypi.org/project/pycatch22/
