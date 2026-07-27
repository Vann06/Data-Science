# Resumen y conclusiones del análisis

Se modeló una única serie: el total mensual de visitantes internacionales a
Guatemala (turistas y excursionistas, excluyendo la etiqueta "Guatemala"),
enero 2009 – junio 2026 (210 observaciones). A continuación se resume, punto
por punto, lo que se hizo y lo que se encontró a lo largo del notebook
(`notebooks/analisis_serie_total_internacional.ipynb`).

## Análisis de la serie de tiempo

- **Gráfico de la serie y sus componentes.** La serie muestra una tendencia de
  crecimiento sostenido, interrumpida por el colapso del turismo durante la
  emergencia sanitaria de 2020 (cinco meses en cero, abril–agosto) y seguida
  de una recuperación que retoma la misma trayectoria previa. La
  descomposición aditiva (período 12) separa tendencia, estacionalidad y
  residuo; el residuo se mantiene estable durante casi todo el período y se
  dispara únicamente durante el choque, lo que confirma que se trata de un
  evento atípico y no de un cambio estructural del proceso generador.

  **[Insertar aquí la imagen de la sección 1.3 — serie total mensual con media móvil de 12 meses]**

  **[Insertar aquí la imagen de la sección 3 — descomposición en tendencia, estacionalidad y residuo]**

- **Estacionalidad.** Sí presenta estacionalidad: el rezago 12 es, de forma
  sistemática, el único rezago relevante tanto en la ACF como en la PACF de
  la serie transformada, con picos en marzo y diciembre y un valle en
  septiembre (amplitud estacional equivalente al 51% de la media de la
  serie). Que exista implica que cualquier modelo debe incorporar
  explícitamente un componente estacional (aquí, una diferencia estacional
  D = 1 con período 12 y un término MA estacional Q = 1); ignorarlo dejaría
  sin explicar una parte sustancial y recurrente de la variación mes a mes.

  **[Insertar aquí la imagen de la sección 3.2 — componente estacional]**

- **Tendencia.** Sí presenta tendencia: la fuerza de tendencia (Hyndman &
  Athanasopoulos) es de 0.80 sobre el entrenamiento completo, claramente
  dominante frente a la estacionalidad, y equivale a un crecimiento
  interanual aproximado del 7% sobre la ventana pre-choque. Esto significa
  que la serie no fluctúa alrededor de un nivel fijo sino que crece de forma
  sostenida en el tiempo, salvo por el quiebre puntual de 2020; por eso el
  modelo final incorpora un término constante que representa esa tasa de
  crecimiento.

  **[Insertar aquí la imagen de la sección 3.1 — componente de tendencia]**

## Determinación de estacionariedad

- **Estacionariedad en varianza.** No es estacionaria en varianza: al dividir
  el entrenamiento en tercios, la desviación estándar crece de forma
  aproximadamente proporcional al nivel de la serie (correlación
  media–desviación de 0.887 sobre los años completos), característica propia
  de un proceso multiplicativo. Se aplicó una **transformación logarítmica
  `log1p`** (y no `log` simple, porque hay meses con valor cero) para
  estabilizarla; tras la transformación la desviación por tercios queda
  prácticamente constante (0.162 vs. 0.165 en T1/T2 sobre la ventana
  pre-choque).

  **[Insertar aquí la imagen de la sección 4.2 — desviación estándar por tercios]**

- **Estacionariedad en media.** Tampoco es estacionaria en media: la media
  móvil de 12 meses varía entre 14,908 y 205,144 visitantes, la ACF en nivel
  decae muy lentamente (32 de 36 rezagos significativos, con valores
  todavía altos en el rezago 24) y la prueba ADF no rechaza la hipótesis de
  raíz unitaria salvo en la especificación con tendencia sobre el
  entrenamiento completo, mientras que KPSS tampoco confirma
  estacionariedad. Con base en la ACF y en ADF/KPSS se determinó que se
  necesita **una diferenciación estacional (D = 1, s = 12)**; se comprobó
  explícitamente, mediante una escalera de diferenciación evaluada con
  ADF/KPSS, que añadir además una diferencia regular (d = 1) **sobre-diferencia**
  la serie (la desviación aumenta en vez de bajar), por lo que se descartó y
  se mantuvo d = 0 con término constante.

  **[Insertar aquí la imagen de la sección 4.3 — ACF de la serie en nivel]**

  **[Insertar aquí la imagen de la sección 5.1 — escalera de diferenciación sobre log1p]**

## Generación de modelos

- **Identificación de p, d, q vía ACF y PACF.** Sobre la serie ya
  transformada (log1p + diferencia estacional), ni la ACF ni la PACF
  muestran rezagos significativos en el corto plazo (1 a 6), por lo que la
  parte no estacional queda vacía: **p = 0, q = 0**. El único rezago
  relevante es el 12, presente en ambas funciones; como la ACF corta en seco
  en el rezago 24 mientras la PACF decae de forma gradual, la regla de
  Box-Jenkins identifica un componente de medias móviles estacional:
  **P = 0, Q = 1**. Con **D = 1** (por el diagnóstico de estacionariedad) y
  d = 0, el modelo resultante es un **SARIMA(0,0,0)(0,1,1)₁₂ con constante**,
  llamado M1 en el notebook.

  **[Insertar aquí la imagen de la sección 6.1 — ACF de la serie transformada]**

  **[Insertar aquí la imagen de la sección 6.2 — PACF de la serie transformada]**

- **Explicación de la elección de parámetros y modelos, incluidos los
  automáticos.** Además de M1 (identificación visual), se ajustó una malla
  automática de 36 combinaciones de órdenes alrededor de esa propuesta
  (sección 8) y un modelo "airline" (0,1,1)(0,1,1)₁₂ clásico (M3), para
  contrastar la lectura manual contra una búsqueda exhaustiva. La malla
  confirma de forma independiente la parte estacional (0,1,1)₁₂ en los cinco
  mejores órdenes; el mejor por AIC agrega dos términos autorregresivos (M2,
  orden (2,0,0)(0,1,1)₁₂), con una mejora de apenas 4.9 puntos de AIC sobre
  M1, evidencia débil frente al costo de dos parámetros adicionales, por lo
  que por parsimonia se prefiere M1. También se comprobó que el ajuste
  depende críticamente de la ventana de entrenamiento: sobre el
  entrenamiento completo (que incluye el choque) ningún coeficiente
  estacional resulta significativo, mientras que sobre la ventana pre-choque
  (2009-01 a 2020-02) los tres coeficientes de M1 son significativos
  (p < 0.001) y sus residuos pasan Ljung-Box.

  **[Insertar aquí la imagen de la sección 7 — ajuste dentro de la muestra: modelos A, B y C]**

- **Modelos generados con los distintos algoritmos.** Se generaron seasonal
  naive (línea base), suavizamiento exponencial simple y Holt-Winters en sus
  variantes aditiva y amortiguada, cada uno sobre la ventana de
  entrenamiento completa y sobre la ventana pre-choque. *Nota:* Prophet no
  estaba disponible en el entorno de ejecución; como el enunciado admite
  cualquiera de las alternativas, se implementaron en su lugar las tres
  restantes.

  **[Insertar aquí la imagen de la sección 10 — pronósticos de los modelos alternativos por ventana]**

- **Comparación por residuos, métricas de error, AIC y BIC.** Los residuos de
  los tres SARIMA sobre la ventana completa fallan la prueba de
  heterocedasticidad y muestran curtosis muy por encima de lo esperado en
  una distribución normal, evidencia de que el choque domina el ajuste;
  sobre la ventana pre-choque los tres pasan Ljung-Box, la heterocedasticidad
  ya no se rechaza y la curtosis baja a un rango razonable. El AIC y el BIC
  solo se compararon dentro de la familia SARIMA, sobre los mismos datos:
  AIC prefiere a M2 y BIC a M3, con M1 muy cerca de ambos; las diferencias
  son pequeñas y no discriminan de forma concluyente dentro de la muestra.
  Frente a Holt-Winters, suavizamiento exponencial y seasonal naive, la
  comparación se hizo exclusivamente con métricas de error sobre el conjunto
  de prueba (sección 11), no con AIC/BIC, porque estos no son comparables
  entre familias de modelos distintas.

  **[Insertar aquí la imagen de la sección 9 — diagnóstico de residuos (ACF, Q-Q) por ventana]**

## Predicción con los modelos generados

- **Conjuntos de entrenamiento y prueba.** Siguiendo el enunciado, la
  partición es cronológica 70/30 sobre el índice completo de la serie (no
  aleatoria, para evitar fuga de información): 147 meses de entrenamiento
  (2009-01 a 2021-03) y 63 de prueba (2021-04 a 2026-06).

  **[Insertar aquí la imagen de la sección 2 — partición 70/30 de la serie]**

- **Qué tan bueno es el modelo prediciendo el conjunto de prueba.** El
  desempeño depende casi por completo de la ventana de entrenamiento, más
  que del algoritmo elegido: los modelos entrenados con toda la serie
  (incluyendo el choque) quedan anclados en el piso pandémico y nunca
  alcanzan el nivel real del conjunto de prueba; su mejor RMSE es 174,266.
  Los modelos entrenados sobre la ventana pre-choque, en cambio, sí capturan
  el nivel y la trayectoria correctos, con RMSE entre 75,695 y 81,574 entre
  los que superan al seasonal naive. Vistos por sub-período, en 2021 (piso
  pandémico) los modelos pre-choque fallan (MAPE superior al 290%), pero a
  partir de 2023 la serie observada entra en la banda de confianza del 95%
  de estos modelos y no vuelve a salir; para 2024-2026, ya con la serie
  normalizada, el mejor modelo alcanza un MAPE de apenas 8.7%.

  **[Insertar aquí la imagen de la sección 11 — comparación de RMSE/MAPE y trayectorias de los mejores modelos]**

  **[Insertar aquí la imagen de la sección 11.1 — métricas segmentadas por sub-período]**

- **Comparación entre los modelos generados con los distintos algoritmos.**
  Sobre el conjunto de prueba, cualquier modelo entrenado en la ventana
  completa resulta peor que el seasonal naive de esa misma ventana y se
  descarta; entre los que sí superan a su línea base, el mejor resultado
  global es **Holt-Winters amortiguado sobre la ventana pre-choque** (RMSE
  75,695, MAE 53,568), seguido muy de cerca por el SARIMA **M1
  (0,0,0)(0,1,1)₁₂ con constante**, también sobre la ventana pre-choque (RMSE
  78,839), la misma especificación identificada manualmente en la sección 6.
  Ambos se usan en la sección 12 para el pronóstico final con intervalos de
  confianza del 95%: M1 obtiene el intervalo mediante la fórmula analítica
  del filtro de Kalman, mientras que Holt-Winters, al no tener una expresión
  cerrada, se aproxima por simulación. Los dos reproducen con precisión la
  forma del ciclo anual desde 2023 en adelante, con Holt-Winters ligeramente
  más ajustado gracias a su mecanismo de moderar la tendencia conforme se
  aleja del último dato observado.

  **[Insertar aquí la imagen de la sección 12 — pronóstico final con intervalos de confianza (vista completa y zoom sobre prueba)]**

**Modelo final seleccionado:** Holt-Winters amortiguado, entrenado sobre la
ventana previa al choque sanitario (2009-01 a 2020-02), con el SARIMA
M1(0,0,0)(0,1,1)₁₂+c como alternativa casi equivalente y con una
interpretación estadística más directa, al derivarse de forma explícita de
la lectura de la ACF y la PACF.
