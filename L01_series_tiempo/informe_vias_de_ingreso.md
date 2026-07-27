# Informe de resultados — Series de tiempo por vías de ingreso

**Universidad del Valle de Guatemala**  
**Facultad de Ingeniería**  
**Departamento de Ciencias de la Computación**  
**CC3084 – Data Science**  
**Semestre II – 2026**

## 1. Descripción general del análisis

Se analizaron tres series mensuales de ingreso de viajeros a Guatemala según la vía utilizada: **Aérea, Terrestre y Marítima**. Cada serie contiene 210 observaciones mensuales comprendidas entre enero de 2009 y junio de 2026.

Para las vías Aérea y Terrestre se utilizaron únicamente los registros clasificados como **Turista** y **Excursionista**, siguiendo el criterio de comparabilidad indicado en las instrucciones. En la vía Marítima se encontró una limitación metodológica: desde 2017 sí existen registros marítimos, pero estos dejaron de aparecer bajo las categorías Turista y Excursionista. Por esta razón, la serie Marítima se construyó utilizando todos los tipos de viajero, evitando sustituir datos existentes por ceros artificiales.

Esta decisión permite analizar el comportamiento marítimo durante todo el período, pero implica que sus volúmenes no son completamente comparables con los de Aérea y Terrestre. Además, los cambios observados en esta serie pueden estar relacionados tanto con variaciones reales como con modificaciones en la clasificación y desagregación de la información.

### Resumen descriptivo de las series

| Vía | Media mensual | Desviación estándar | Mínimo | Máximo | Meses con cero |
|---|---:|---:|---:|---:|---:|
| Aérea | 90,568.66 | 27,855.30 | 489.00 | 158,463.00 | 0 |
| Terrestre | 131,391.68 | 60,815.99 | 5,240.00 | 291,272.07 | 0 |
| Marítima | 5,851.34 | 6,708.80 | 0.00 | 29,506.00 | 27 |

Las gráficas exploratorias muestran que Aérea y Terrestre presentan patrones más continuos, con crecimiento antes de 2020, una caída fuerte durante la pandemia y una recuperación posterior. Marítima presenta cambios más abruptos, mayor dispersión relativa y períodos con valores iguales a cero. En las tres vías, diciembre fue el mes con mayor flujo promedio.

## 2. División en entrenamiento y prueba

La división se realizó respetando el orden temporal de las observaciones, sin mezclar meses pasados y futuros.

| Conjunto | Período | Meses | Porcentaje |
|---|---|---:|---:|
| Entrenamiento | Enero 2009 – marzo 2021 | 147 | 70 % |
| Prueba | Abril 2021 – junio 2026 | 63 | 30 % |

El mismo punto de corte se aplicó a las tres series. En el caso de Marítima, después de corregir su construcción, el conjunto de prueba contiene 52 meses con valores positivos y 11 meses con cero, por lo que ya no queda compuesto artificialmente únicamente por ceros.

---

# 3. Generación de modelos

## 3.1 Serie Aérea

La serie Aérea presentó una **estacionalidad moderada**, con una fuerza estacional de 0.384, y una tendencia importante, con una fuerza de tendencia de 0.613. La prueba Dickey-Fuller aumentada aplicada a la serie original produjo un valor p de 0.15, por lo que no se consideró estacionaria en media.

La transformación logarítmica no mejoró la estabilidad de la varianza, por lo que la serie se conservó en su escala original. Para alcanzar estacionariedad se aplicó una diferencia regular, obteniendo **d = 1** y **D = 0**. Después de diferenciar, la prueba ADF produjo un valor p cercano a cero.

La función de autocorrelación parcial sugirió **p = 2**, mientras que la función de autocorrelación sugirió **q = 2**. A partir de estos resultados se compararon diferentes modelos ARIMA y SARIMA cercanos. El mejor candidato de esta familia fue:

**SARIMA (0,1,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 2,869.86, un BIC de 2,884.24 y un valor p de Ljung-Box de 0.65 en entrenamiento, lo que indica que sus residuos no conservaron autocorrelación significativa dentro del conjunto utilizado para ajustarlo.

También se generaron los modelos Prophet, Holt-Winters, suavizamiento exponencial y Seasonal Naive. Los resultados sobre el conjunto de prueba fueron:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Suavizamiento exponencial | 36,970.60 | 42,141.22 |
| Prophet | 41,271.36 | 45,655.27 |
| Holt-Winters | 43,072.93 | 47,051.02 |
| Seasonal Naive | 75,512.73 | 79,339.80 |
| ARIMA/SARIMA | 74,524.43 | 79,593.05 |

El mejor resultado fue obtenido por **suavizamiento exponencial**, debido a que presentó los menores valores de MAE y RMSE. Sin embargo, los residuos del conjunto de prueba conservaron autocorrelación significativa, por lo que el modelo todavía dejó patrones temporales sin explicar completamente.

## 3.2 Serie Terrestre

La serie Terrestre presentó una **estacionalidad moderada**, con una fuerza de 0.409, y la tendencia más fuerte de las tres vías, con un valor de 0.818. La prueba ADF aplicada a la serie original produjo un valor p de 0.24, indicando que no era estacionaria.

La transformación logarítmica no produjo una mejora suficiente en la estabilidad de la varianza, por lo que se conservó la escala original. Se aplicó una diferencia regular, obteniendo **d = 1** y **D = 0**. Después de la diferenciación, la prueba ADF produjo un valor p de 0.01, confirmando la estacionariedad en media.

La PACF sugirió **p = 3**, mientras que la ACF sugirió **q = 2**. Después de comparar diferentes combinaciones, el mejor modelo de la familia ARIMA/SARIMA fue:

**SARIMA (0,1,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 3,091.31, un BIC de 3,105.69 y un valor p de Ljung-Box de 0.55 en entrenamiento. Por lo tanto, sus residuos de entrenamiento no mostraron autocorrelación significativa.

Los modelos comparados en prueba presentaron los siguientes resultados:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Prophet | 47,713.21 | 57,657.61 |
| Suavizamiento exponencial | 121,715.64 | 134,136.23 |
| Holt-Winters | 128,421.20 | 139,161.45 |
| Seasonal Naive | 132,209.04 | 144,274.98 |
| ARIMA/SARIMA | 147,398.53 | 158,502.92 |

El mejor modelo fue **Prophet**, con una diferencia amplia respecto de los demás algoritmos. Este resultado sugiere que su capacidad para representar cambios de tendencia fue más adecuada para una serie afectada por el choque de 2020 y la recuperación posterior. A pesar de obtener los menores errores, sus residuos de prueba conservaron autocorrelación significativa.

## 3.3 Serie Marítima

La serie Marítima presentó la **mayor fuerza estacional**, con un valor de 0.641, y una fuerza de tendencia moderada de 0.576. También mostró la mayor variabilidad relativa y un comportamiento considerablemente más irregular que las otras vías.

La relación entre el nivel de la serie y su variabilidad fue alta, por lo que se aplicó la transformación **log1p**. La prueba ADF de la serie transformada produjo un valor p de 1.00, por lo que fue necesario aplicar dos diferencias regulares. Los valores seleccionados fueron **d = 2** y **D = 0**. Después de diferenciar, el valor p de la prueba ADF fue cercano a cero.

La PACF sugirió **p = 3** y la ACF sugirió **q = 2**. El mejor candidato ARIMA/SARIMA fue:

**SARIMA (0,2,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 551.92, un BIC de 566.26 y un valor p de Ljung-Box de 0.07 en entrenamiento. Entre los candidatos evaluados, fue uno de los modelos que combinó valores bajos de AIC y BIC con residuos sin autocorrelación significativa al nivel de 5 %.

Los resultados de prueba fueron:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Holt-Winters | 902.62 | 1,685.06 |
| Suavizamiento exponencial | 858.37 | 1,731.93 |
| Seasonal Naive | 858.37 | 1,731.93 |
| ARIMA/SARIMA | 858.37 | 1,731.93 |
| Prophet | 7,272.58 | 8,587.77 |

Aunque varios modelos obtuvieron un MAE ligeramente menor, **Holt-Winters** presentó el menor RMSE, un sesgo relativamente bajo y residuos de prueba sin autocorrelación significativa, con un valor p de Ljung-Box de 0.19. Por estas razones fue seleccionado como el modelo más adecuado para esta serie.

Los errores de Marítima no deben compararse directamente con los de Aérea y Terrestre, debido a la diferencia de escala y a la limitación metodológica de su construcción.

### Comparación de los modelos seleccionados

| Vía | Mejor modelo | MAE | RMSE | Autocorrelación en residuos de prueba |
|---|---|---:|---:|---|
| Aérea | Suavizamiento exponencial | 36,970.60 | 42,141.22 | Sí |
| Terrestre | Prophet | 47,713.21 | 57,657.61 | Sí |
| Marítima | Holt-Winters | 902.62 | 1,685.06 | No significativa |

El análisis demuestra que no existe un único algoritmo que funcione mejor para todas las vías. Cada serie necesitó un modelo diferente de acuerdo con su tendencia, estacionalidad, variabilidad y presencia de cambios estructurales.

AIC y BIC se utilizaron principalmente para comparar candidatos ARIMA/SARIMA y modelos de suavizamiento cuando estas métricas estaban disponibles. Prophet y Seasonal Naive se compararon principalmente mediante los errores obtenidos en el conjunto de prueba y el comportamiento de los residuos.

---

# 4. Predicción con los modelos generados

Los modelos se ajustaron con las 147 observaciones de entrenamiento y se evaluaron sobre 63 meses que no participaron en su estimación. La comparación se realizó mediante MAE, RMSE, sesgo promedio y la prueba de Ljung-Box aplicada a los residuos.

Para Aérea, el suavizamiento exponencial presentó el mejor desempeño de prueba. Sin embargo, el RMSE de 42,141.22 representa un error relevante frente a una media mensual de 90,568.66. Además, los residuos conservaron autocorrelación, por lo que el modelo no capturó completamente la recuperación posterior a la pandemia.

Para Terrestre, Prophet obtuvo el menor error, con un RMSE de 57,657.61. Frente a una media mensual de 131,391.68, el error sigue siendo considerable, pero fue claramente inferior al de los demás algoritmos. La existencia de autocorrelación en los residuos indica que todavía quedaron patrones por explicar.

Para Marítima, Holt-Winters obtuvo un RMSE de 1,685.06 frente a una media mensual de 5,851.34. Sus residuos no conservaron autocorrelación significativa, lo que indica que capturó de mejor forma la estructura temporal disponible en el conjunto de prueba. Aun así, la predicción marítima debe considerarse exploratoria debido a los cambios metodológicos de la serie.

En general, los modelos permiten aproximar el comportamiento de los ingresos migratorios, pero no deben utilizarse como predicciones exactas. La pandemia produjo un quiebre estructural importante y el período de prueba incluye una recuperación diferente del comportamiento observado en buena parte del entrenamiento. Por ello, los pronósticos deben actualizarse periódicamente con nueva información.

---

# 5. Análisis comparativo de las vías

| Vía | Fuerza estacional | Fuerza de tendencia | Coeficiente de variación | Pendiente mensual relativa antes de 2020 | Cambio 2020 frente a 2019 |
|---|---:|---:|---:|---:|---:|
| Aérea | 0.384 | 0.613 | 0.31 | 0.43 % | −72.80 % |
| Terrestre | 0.409 | 0.818 | 0.46 | 0.87 % | −75.23 % |
| Marítima | 0.641 | 0.576 | 1.15 | 0.44 % | −67.89 % |

## 5.1 ¿Cuál vía presenta mayor estacionalidad?

La vía **Marítima** presentó la mayor fuerza estacional, con un valor de 0.641. Esto indica que su flujo depende en mayor medida del mes del año. Aérea y Terrestre también presentaron patrones estacionales, pero con menor intensidad.

## 5.2 ¿Cuál vía presenta mayor tendencia de crecimiento?

La vía **Terrestre** presentó la tendencia más fuerte, con un valor de 0.818, y la mayor pendiente mensual relativa antes de la pandemia, equivalente a aproximadamente 0.87 %. Aérea presentó una pendiente relativa de 0.43 % y Marítima de 0.44 %.

## 5.3 ¿Cuál vía presenta mayor volatilidad?

La vía **Marítima** presentó la mayor volatilidad relativa, con un coeficiente de variación de 1.15. Este resultado es considerablemente superior al de Terrestre, con 0.46, y Aérea, con 0.31. La elevada dispersión marítima puede estar relacionada tanto con la naturaleza de este flujo como con los cambios metodológicos documentados.

## 5.4 ¿Cuál vía fue más afectada por la pandemia?

La vía **Terrestre** presentó la mayor caída entre 2019 y 2020, con una reducción de 75.23 %. La vía Aérea disminuyó 72.80 % y Marítima 67.89 %. Estos resultados muestran que las restricciones de movilidad afectaron especialmente los ingresos por fronteras terrestres.

## 5.5 Comparación general

Aérea fue la serie menos volátil y presentó un comportamiento relativamente más estable. Terrestre mostró el mayor crecimiento previo a la pandemia, pero también la caída porcentual más fuerte en 2020. Marítima presentó la mayor estacionalidad y volatilidad, además de cambios de clasificación que reducen su comparabilidad directa.

---

# 6. Descubrimientos útiles para INGUAT

1. **Diciembre es el mes con mayor flujo promedio en las tres vías.** Este patrón puede utilizarse para anticipar una mayor demanda de personal, información turística, transporte y atención en puntos de ingreso.

2. **La vía Terrestre tiene el mayor crecimiento de largo plazo.** Antes de la pandemia presentó la pendiente relativa más alta, por lo que puede representar un canal prioritario para acciones dirigidas a visitantes regionales.

3. **Terrestre también fue la vía más sensible a la pandemia.** La reducción de 75.23 % demuestra que los flujos fronterizos terrestres pueden verse especialmente afectados por restricciones de movilidad y cierres fronterizos.

4. **Aérea presenta la menor volatilidad relativa.** Su comportamiento más estable permite construir proyecciones con menor variación, aunque la recuperación posterior a 2020 todavía generó errores importantes.

5. **Marítima requiere una revisión de calidad y consistencia de datos.** Los cambios en la clasificación desde 2017 dificultan la comparación histórica. Para mejorar futuros análisis, sería conveniente mantener definiciones homogéneas y documentar claramente cualquier cambio en las categorías.

6. **Los modelos deben actualizarse con frecuencia.** Los residuos de Aérea y Terrestre conservaron autocorrelación en prueba, lo que muestra que todavía existen patrones no capturados. La incorporación de nuevos meses puede mejorar los parámetros y reducir el error.

7. **No debe utilizarse el mismo modelo para todas las vías.** Suavizamiento exponencial fue mejor para Aérea, Prophet para Terrestre y Holt-Winters para Marítima. Esto demuestra la necesidad de una estrategia de pronóstico diferenciada.

8. **Las predicciones deben acompañarse de intervalos y escenarios.** Debido a la pandemia, la recuperación y los cambios metodológicos, es más prudente interpretar los pronósticos como rangos de planificación y no como valores exactos.

---

# 7. Conclusiones

Las tres vías de ingreso presentan comportamientos diferentes y requieren tratamientos estadísticos específicos. Aérea mostró una estacionalidad moderada, una tendencia importante y la menor volatilidad relativa. Terrestre presentó la tendencia de crecimiento más fuerte y el mayor impacto de la pandemia. Marítima fue la más estacional y volátil, pero sus resultados están condicionados por cambios metodológicos en la clasificación de los viajeros.

Las transformaciones y diferenciaciones permitieron alcanzar estacionariedad antes de ajustar los modelos. Aérea y Terrestre no necesitaron transformación logarítmica y alcanzaron estacionariedad con una diferencia regular. Marítima necesitó una transformación log1p y dos diferencias regulares.

Los parámetros ARIMA/SARIMA fueron propuestos mediante ACF, PACF y pruebas de estacionariedad, y posteriormente se compararon diferentes candidatos con AIC, BIC y diagnóstico de residuos. Además, se evaluaron Prophet, Holt-Winters, suavizamiento exponencial y Seasonal Naive bajo el mismo conjunto de prueba.

El mejor modelo fue diferente para cada serie: suavizamiento exponencial para Aérea, Prophet para Terrestre y Holt-Winters para Marítima. Los resultados confirman que la selección debe realizarse según las características de cada flujo. No obstante, la autocorrelación presente en los residuos de Aérea y Terrestre indica que las predicciones todavía pueden mejorarse.

Finalmente, los modelos pueden apoyar la planificación de INGUAT, especialmente para anticipar meses de mayor flujo, identificar vías con crecimiento importante y evaluar la sensibilidad ante choques externos. Su uso debe complementarse con actualizaciones frecuentes y con una mejora en la consistencia del registro marítimo.
