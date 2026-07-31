# Informe de resultados — Series de tiempo de viajeros internacionales a Guatemala

**Universidad del Valle de Guatemala**
**Facultad de Ingeniería**
**Departamento de Ciencias de la Computación**
**CC3084 – Data Science**
**Semestre II – 2026**
**Ricardo Godinez -23247**
**Vianka Castro -23201**
**Sebastian Bustamante -22291**

Este informe reúne el análisis de las **siete series mensuales** construidas
para el laboratorio: la serie **total** de viajeros internacionales
(`notebooks/analisis_serie_total_internacional.ipynb`), las tres series por
**vía de ingreso** — Aérea, Terrestre y Marítima
(`notebooks/vias_de_ingreso.ipynb`) — y las tres series por **región
geográfica** de origen — América del Centro, América del Norte y Europa
(`notebooks/Analisis_zonas_geograficas.ipynb`). Se organiza siguiendo los
cuatro bloques de la rúbrica del laboratorio (análisis de la serie,
estacionariedad, generación de modelos y predicción), aplicados a cada una
de las series. Antes de entrar a las series, la sección 0 resume el
diagnóstico exploratorio (`notebooks/analisis_exploratorio.ipynb`) que
justifica las decisiones de comparabilidad, calidad de datos y construcción
que se usan en el resto del documento.

---

## 0. Análisis exploratorio de los datos

### 0.1 Fuente, comparabilidad y calidad de los datos

La base original está en formato largo: cada fila combina año, mes, vía,
frontera, país, región y tipo de viajero, con el conteo correspondiente en
`Viajero`. Cubre enero de 2009 a junio de 2026.

De las cuatro categorías de `Tipo de Viajero`, **Turista** (71.99% del
acumulado) y **Excursionista** (17.34%) se mantienen consistentes en toda la
serie; `Cruceristas` (2.11%) deja de reportarse desde 2023 y `Viajero`
(8.55%) se reclasifica ese mismo año por un cambio metodológico. Por eso
las series de este laboratorio usan únicamente Turista y Excursionista, lo
que deja 137,642 registros y 46,711,913 visitantes acumulados. *Esta cifra
todavía incluye la etiqueta de país "Guatemala"; su exclusión adicional se
decide y se justifica en la sección 1.1, al construir la serie total
internacional definitiva.*

La calidad de los datos es alta: no hay valores faltantes, duplicados
exactos, fechas inválidas ni cantidades negativas, y la cobertura mensual
es completa (210 de 210 meses esperados, 0 ausentes). Existen 54
combinaciones en cero, que se conservan porque representan combinaciones
válidas sin flujo observado y no errores de captura.

### 0.2 Estadísticas descriptivas: nivel fila vs. nivel mensual

A nivel de registro individual la distribución es muy asimétrica (media de
339 visitantes, mediana de 7, máximo de 83,511): hay muchas combinaciones
pequeñas y pocas de gran volumen. La escala relevante para modelar es la
agregación mensual: media de 222,438 visitantes, desviación estándar de
84,725, mínimo de 9,779, máximo de 449,114 y un coeficiente de variación de
38.09%. Esta dispersión no debe interpretarse como ruido aleatorio: refleja
crecimiento, estacionalidad, el choque de 2020 y la recuperación posterior.

### 0.3 Comportamiento temporal agregado

La media móvil de 12 meses muestra una trayectoria creciente con
oscilaciones anuales antes de 2020, una caída abrupta desde marzo de ese
año y una recuperación posterior clara.

![Visitantes internacionales comparables por mes, con media móvil de 12 meses](img/explor_media_movil.png)

La comparación anual indexada a 2019 = 100 cuantifica el choque y la
recuperación: 2020 cae a 25.65 (−74.35% frente a 2019) y 2021 apenas sube a
26.59. El +193.85% de 2022 es engañoso si se lee de forma aislada, porque
parte de una base extremadamente baja — en el índice equivale apenas a
78.15, todavía por debajo de 2019. Para 2024 y 2025 el índice se estabiliza
en 79–81, sin llegar a 100 en esta versión preliminar de la serie (2026
solo cubre seis meses y no es comparable con años completos). *Este
resultado corresponde a la base "con Guatemala"; al excluir esa etiqueta
más adelante, la recuperación resulta más completa (sección 1.1).*

### 0.4 Concentración geográfica: países y regiones

El flujo está fuertemente concentrado: El Salvador (30.14%) y Guatemala
(29.69%, residentes que reingresan al país) encabezan el acumulado por
país, seguidos de Estados Unidos (14.91%) y Honduras (5.40%). Por región,
**América del Centro** domina con 71.25% del acumulado, seguida de
**América del Norte** (19.61%) y **Europa** (4.60%); el resto de regiones
no supera el 3.1% cada una.

![Diez países y regiones con mayor acumulado](img/explor_top_paises_regiones.png)

### 0.5 Vías y fronteras de ingreso

La vía **Terrestre** concentra 59.07% del acumulado (27.6 millones) y la
**Aérea** 40.72% (19.0 millones); la **Marítima** apenas 0.21% (100 mil) —
lo que anticipa por qué esa vía requirió un tratamiento de datos distinto
en el resto del laboratorio. Por frontera, La Aurora (el aeropuerto)
concentra 40.65% del acumulado y Valle Nuevo (frontera con El Salvador)
21.71%, seguidas de San Cristóbal, Pedro de Alvarado y La Ermita.

![Volumen acumulado por vía y diez fronteras con mayor acumulado](img/explor_top_vias_fronteras.png)

### 0.6 Cruce entre región y vía de ingreso

El cruce entre región y vía revela dos patrones de acceso claramente
distintos: América del Centro ingresa mayoritariamente por **tierra**
(73.8%, frente a 26.0% aérea), mientras que América del Norte (80.0%
aérea), América del Sur y el Caribe (83.2% aérea) y Europa (64.2% aérea)
dependen sobre todo de la **conectividad aérea**.

![Distribución de cada región por vía de ingreso](img/explor_cruce_region_via.png)

Esta composición explica por qué, más adelante, los hallazgos de la vía
Terrestre y de la región América del Centro tienden a coincidir (comparten
el mismo canal dominante), y por qué la vía Aérea se parece más al
comportamiento de América del Norte y Europa.

### 0.7 Valores atípicos

A nivel de registro individual, 16.63% de los 137,642 registros supera el
límite superior del criterio IQR — esperable dada la fuerte asimetría de
una base tan granular, y no se eliminan porque corresponden a combinaciones
legítimas de alto volumen. A nivel mensual, en cambio, solo **un mes**
queda marcado como atípico: diciembre de 2019, con 449,114 visitantes, el
pico histórico justo antes de la pandemia. Se conserva porque corresponde a
un mes real y estacionalmente fuerte, no a un error de datos.

![Distribución por registro y de los totales mensuales](img/explor_outliers.png)

### 0.8 De la exploración a las series de tiempo

A partir de este diagnóstico se construyeron las **siete series mensuales**
analizadas en el resto del informe: la serie total, las tres vías de
ingreso y las tres regiones con mayor acumulado (América del Centro,
América del Norte y Europa, determinadas con el período completo para que
el ranking no dependa de un año en particular). Todas comparten el mismo
inicio, fin y frecuencia mensual, y la misma partición cronológica 70/30
(147 meses de entrenamiento, 63 de prueba) detallada en la sección 2.

---

## 1. Series analizadas

### 1.1 Serie total internacional

Se construyó a partir de los registros clasificados como **Turista** o
**Excursionista**, excluyendo la etiqueta de país **Guatemala** (residentes
que reingresan al país). Ambos filtros responden a un problema de
comparabilidad temporal: la fuente cambia de metodología en 2023 y, sin
filtrarlos, la serie mezclaría universos distintos (`Cruceristas` deja de
reportarse desde 2023, `Viajero` se reclasifica y pierde ~70% de nivel, y la
etiqueta `Guatemala` desaparece por completo desde enero de 2023). El
resultado es una serie mensual de 210 observaciones, de enero de 2009 a junio
de 2026.

Al excluir la etiqueta `Guatemala`, la caída y la recuperación quedan más
claras que en la vista preliminar de la sección 0.3: con índice 2019 = 100,
2020 baja a **22.73** (−77.3%), pero para 2024 el índice ya alcanza
**134.82** (+34.8% sobre 2019) y en 2025 sube a 138.02 — es decir, esta
versión de la serie no solo se recuperó, sino que superó ampliamente su
nivel prepandemia.

### 1.2 Series por vía de ingreso

Se analizaron tres series mensuales de ingreso de viajeros a Guatemala según
la vía utilizada: **Aérea, Terrestre y Marítima**, cada una con las mismas
210 observaciones mensuales. Para Aérea y Terrestre se usó el mismo criterio
de comparabilidad (Turista y Excursionista). En la vía Marítima se encontró
una limitación metodológica: desde 2017 existen registros marítimos, pero
dejaron de aparecer bajo las categorías Turista y Excursionista. Por ello, la
serie Marítima se construyó con todos los tipos de viajero, para no sustituir
datos existentes por ceros artificiales; esto permite analizar su
comportamiento durante todo el período, pero implica que sus volúmenes no son
completamente comparables con los de Aérea y Terrestre, ni con la serie total
(que sí aplica el filtro Turista/Excursionista de forma estricta).

### 1.3 Series por región geográfica

Se analizaron también tres series mensuales según la región geográfica de
origen de los visitantes, seleccionadas por ser las de mayor volumen
acumulado en todo el período: **América del Centro, América del Norte y
Europa**. Al igual que en las vías, se usó el criterio Turista/Excursionista
para mantener comparabilidad temporal. Las tres regiones cubren exactamente
el mismo período (enero 2009 – junio 2026, 210 meses), con la misma
partición 70/30 (147 meses de entrenamiento, 63 de prueba) y sin meses
faltantes.

| Región | Inicio entrenamiento | Fin entrenamiento | Inicio prueba | Fin prueba | Meses entrenamiento | Meses prueba | Meses faltantes |
|---|---|---|---|---|---:|---:|---:|
| América del Centro | 2009-01 | 2021-03 | 2021-04 | 2026-06 | 147 | 63 | 0 |
| América del Norte | 2009-01 | 2021-03 | 2021-04 | 2026-06 | 147 | 63 | 0 |
| Europa | 2009-01 | 2021-03 | 2021-04 | 2026-06 | 147 | 63 | 0 |

América del Centro concentra el mayor volumen y una fuerte relación con el
ingreso terrestre; América del Norte y Europa presentan niveles menores pero
mayor dependencia de la conectividad aérea. En las tres regiones la caída de
2020 constituye una ruptura estructural y no una fluctuación estacional
normal.

![Comportamiento mensual de las tres regiones geográficas](img/region_figura_1_series_regionales.png)

**Resumen descriptivo (serie total y vías):**

| Serie | Media mensual | Desviación estándar | Mínimo | Máximo | Meses con cero |
|---|---:|---:|---:|---:|---:|
| Total internacional | 156,388.20 | 74,176.33 | 0.00 | 365,573.02 | 5 |
| Aérea | 90,568.66 | 27,855.30 | 489.00 | 158,463.00 | 0 |
| Terrestre | 131,391.68 | 60,815.99 | 5,240.00 | 291,272.07 | 0 |
| Marítima | 5,851.34 | 6,708.80 | 0.00 | 29,506.00 | 27 |

Las cuatro series comparten el mismo patrón general: crecimiento antes de
2020, una caída fuerte durante la pandemia y una recuperación posterior que,
en todos los casos, retoma la trayectoria previa al choque. Diciembre fue el
mes con mayor flujo promedio en las tres vías.

![Serie total mensual con media móvil de 12 meses](img/total_cell08_0.png)

---

## 2. División en entrenamiento y prueba

La partición se hizo de forma **cronológica**, no aleatoria, para evitar
fuga de información: el 70% inicial de los 210 meses para entrenamiento y el
30% final para prueba. El mismo punto de corte se aplicó a las **cuatro
series**.

| Conjunto | Período | Meses | Porcentaje |
|---|---|---:|---:|
| Entrenamiento | Enero 2009 – marzo 2021 | 147 | 70% |
| Prueba | Abril 2021 – junio 2026 | 63 | 30% |

En el caso de Marítima, después de corregir su construcción, el conjunto de
prueba contiene 52 meses con valores positivos y 11 meses en cero, por lo que
ya no queda compuesto artificialmente solo por ceros. En la serie total,
cinco meses del entrenamiento (abril–agosto de 2020) quedan en cero por el
cierre de fronteras. La misma partición se aplicó a las tres series
regionales, que también cubren exactamente 147 meses de entrenamiento y 63
de prueba, sin meses faltantes (ver Tabla en la sección 1.3).

![Partición 70/30 de la serie total](img/total_cell14_0.png)

---

## 3. Análisis de las series de tiempo

Para cada serie se revisa su gráfico y componentes, si presenta
estacionalidad (y qué implica) y si presenta tendencia (y qué significa).

### 3.1 Serie total internacional

La serie muestra una tendencia de crecimiento sostenido, interrumpida por el
colapso del turismo durante la emergencia sanitaria de 2020 (cinco meses en
cero) y seguida de una recuperación que retoma la misma trayectoria previa.
La descomposición aditiva (período 12) separa tendencia, estacionalidad y
residuo; el residuo se mantiene estable durante casi todo el período y se
dispara únicamente durante el choque, lo que confirma que se trata de un
evento atípico y no de un cambio estructural del proceso generador.

- **Estacionalidad:** sí presenta. El rezago 12 es, de forma sistemática, el
  único rezago relevante tanto en la ACF como en la PACF de la serie
  transformada, con picos en marzo y diciembre y un valle en septiembre
  (amplitud estacional equivalente al 51% de la media de la serie). La
  fuerza de estacionalidad (Hyndman & Athanasopoulos) es de 0.46 sobre el
  entrenamiento completo y sube a 0.73 al excluir el choque de 2020, que
  distorsiona el patrón anual. Esto implica que el modelo debe incorporar
  un componente estacional explícito (una diferencia estacional D = 1 con
  período 12 y un término MA estacional Q = 1); ignorarlo dejaría sin
  explicar una parte recurrente y sustancial de la variación mes a mes.
- **Tendencia:** sí presenta. La fuerza de tendencia es de 0.80 sobre el
  entrenamiento completo y de 0.88 al excluir el choque, claramente
  dominante frente a la estacionalidad en ambos casos, y equivale a un
  crecimiento interanual aproximado del 7% sobre la ventana pre-choque.
  Esto significa que la serie no fluctúa alrededor de un nivel fijo, sino
  que crece de forma sostenida en el tiempo salvo por el quiebre puntual de
  2020; por eso el modelo final incorpora un término constante que
  representa esa tasa de crecimiento.

![Descomposición en tendencia, estacionalidad y residuo — Total internacional](img/total_cell17_0.png)

### 3.2 Serie Aérea

- **Estacionalidad:** presenta una estacionalidad **moderada**, con fuerza de
  0.384. Es un componente presente pero no dominante: el flujo aéreo depende
  del mes del año, con diciembre como el mes de mayor volumen, pero en menor
  medida que las otras dos vías.
- **Tendencia:** presenta una tendencia **importante**, con fuerza de 0.613,
  y una pendiente mensual relativa de 0.43% antes de 2020. Significa que el
  turismo aéreo venía en expansión sostenida antes de la pandemia, aunque de
  forma más moderada que la vía terrestre.

![Gráfico y componentes — Serie Aérea](img/aerea_diag_0.png)

![Gráfico y componentes — Serie Aérea](img/aerea_diag_1.png)

### 3.3 Serie Terrestre

- **Estacionalidad:** presenta una estacionalidad **moderada**, con fuerza de
  0.409, similar a la de Aérea.
- **Tendencia:** presenta la tendencia **más fuerte de las tres vías**, con
  un valor de 0.818 y la mayor pendiente mensual relativa antes de la
  pandemia (0.87%). Esto significa que el ingreso terrestre fue el canal con
  mayor crecimiento estructural en el largo plazo, previo al choque de 2020.

![Gráfico y componentes — Serie Terrestre](img/terrestre_diag_0.png)

![Gráfico y componentes — Serie Terrestre](img/terrestre_diag_1.png)

### 3.4 Serie Marítima

- **Estacionalidad:** presenta la **mayor fuerza estacional** de las cuatro
  series, con un valor de 0.641. Implica que el flujo marítimo depende en
  mayor medida del mes del año que el resto de vías, y que un modelo sin
  componente estacional explicaría mal su comportamiento.
- **Tendencia:** presenta una tendencia **moderada**, con fuerza de 0.576 y
  una pendiente mensual relativa de 0.44% antes de 2020, similar a la de
  Aérea. También es la serie con mayor variabilidad relativa (coeficiente de
  variación de 1.15) y con un comportamiento considerablemente más irregular,
  en parte por la limitación de datos descrita en la sección 1.2.

![Gráfico y componentes — Serie Marítima](img/maritima_diag_0.png)

![Gráfico y componentes — Serie Marítima](img/maritima_diag_1.png)

### 3.5 Región América del Centro

- **Estacionalidad:** fuerza de 0.36 dentro del entrenamiento completo
  (sube a 0.69 si se excluye la pandemia, ver sección 7.2), con diciembre
  como mes de mayor actividad y septiembre como el más bajo. El patrón
  aparece menos regular que en las otras regiones porque la magnitud del
  choque de 2020 se mezcla con el residuo.
- **Tendencia:** fuerza de 0.77 dentro del entrenamiento completo, la
  segunda más alta de las tres regiones. Implica un crecimiento pronunciado
  antes de 2020, seguido de una caída que se refleja principalmente en la
  tendencia y en el residuo, por no ser un patrón que se repita cada año.

![Descomposición de América del Centro](img/region_figura_2_descomposicion_centro.png)

### 3.6 Región América del Norte

- **Estacionalidad:** fuerza de 0.57 dentro del entrenamiento completo, con
  diciembre como mes de mayor actividad y septiembre como el más bajo — un
  ciclo anual más claro que el de América del Centro.
- **Tendencia:** fuerza de 0.64, la más moderada de las tres regiones. El
  residuo aumenta de forma considerable durante la ruptura de 2020, señal
  de que ese evento no queda explicado ni por la tendencia ni por la
  estacionalidad.

![Descomposición de América del Norte](img/region_figura_3_descomposicion_norte.png)

### 3.7 Región Europa

- **Estacionalidad:** presenta la mayor fuerza estacional de las tres
  regiones dentro del entrenamiento, con 0.76, y el patrón más regular. A
  diferencia de las otras dos, su pico ocurre en febrero y su valle en
  junio.
- **Tendencia:** presenta la mayor fuerza de tendencia de las tres
  regiones, con 0.81. Igual que en el resto de series, la pandemia produce
  una desviación que la estacionalidad normal no puede explicar.

![Descomposición de Europa](img/region_figura_4_descomposicion_europa.png)

---

## 4. Determinación de estacionariedad

Para cada serie se evalúa si es estacionaria en varianza (aplicando una
transformación si no lo es) y si es estacionaria en media (con ACF y la
prueba ADF), determinando cuántas diferenciaciones se necesitan.

### 4.1 Serie total internacional

**Varianza.** No es estacionaria en varianza: al dividir el entrenamiento en
tercios, la desviación estándar crece de forma aproximadamente proporcional
al nivel de la serie (correlación media–desviación de 0.887), característica
propia de un proceso multiplicativo. Se aplicó una **transformación
logarítmica `log1p`** (y no `log` simple, porque hay meses con valor cero);
tras la transformación la desviación por tercios queda prácticamente
constante.

**Media.** Tampoco es estacionaria en media: la media móvil de 12 meses
varía entre 14,908 y 205,144 visitantes, la ACF en nivel decae de forma
lenta (9 de 36 rezagos significativos, con ACF(1) = 0.80 y el primer
rezago no significativo hasta el 10) y la prueba ADF no rechaza la raíz
unitaria salvo en una especificación puntual, mientras KPSS tampoco
confirma estacionariedad. Se determinó que se necesita **una diferenciación
estacional (D = 1, s = 12)**; se comprobó explícitamente, mediante una
escalera de diferenciación evaluada con ADF/KPSS, que añadir además una
diferencia regular (d = 1) sobre-diferencia la serie (la desviación aumenta
en vez de bajar), por lo que se descartó y se mantuvo **d = 0** con término
constante.

![ACF de la serie en nivel — Total internacional](img/total_cell44_0.png)

![Escalera de diferenciación sobre log1p — Total internacional](img/total_cell49_0.png)

### 4.2 Serie Aérea

**Varianza.** La transformación logarítmica no mejoró la estabilidad de la
varianza, por lo que la serie se conservó en su escala original.

**Media.** La prueba ADF aplicada a la serie original produjo un valor p de
0.15, por lo que no se consideró estacionaria en media. Para alcanzar
estacionariedad se aplicó **una diferencia regular (d = 1, D = 0)**; después
de diferenciar, la prueba ADF produjo un valor p cercano a cero, confirmando
la estacionariedad.

![Estacionariedad en varianza y en media — Serie Aérea](img/aerea_diag_2.png)

![Estacionariedad en varianza y en media — Serie Aérea](img/aerea_diag_3.png)

### 4.3 Serie Terrestre

**Varianza.** Al igual que en Aérea, la transformación logarítmica no
produjo una mejora suficiente en la estabilidad de la varianza, por lo que
se conservó la escala original.

**Media.** La prueba ADF sobre la serie original produjo un valor p de 0.24,
indicando que no era estacionaria. Se aplicó **una diferencia regular
(d = 1, D = 0)**; después de diferenciar, la prueba ADF produjo un valor p de
0.01, confirmando la estacionariedad en media.

![Estacionariedad en varianza y en media — Serie Terrestre](img/terrestre_diag_2.png)

![Estacionariedad en varianza y en media — Serie Terrestre](img/terrestre_diag_3.png)

### 4.4 Serie Marítima

**Varianza.** A diferencia de Aérea y Terrestre, la relación entre el nivel
de la serie y su variabilidad fue alta, por lo que se aplicó la
transformación **log1p**.

**Media.** La prueba ADF de la serie transformada produjo un valor p de
1.00, por lo que fue necesario aplicar **dos diferencias regulares**: los
valores seleccionados fueron **d = 2, D = 0**. Después de diferenciar, el
valor p de la prueba ADF fue cercano a cero. Es, de las cuatro series, la que
requirió mayor grado de diferenciación.

![Estacionariedad en varianza y en media — Serie Marítima](img/maritima_diag_2.png)

![Estacionariedad en varianza y en media — Serie Marítima](img/maritima_diag_3.png)

### 4.5 Región América del Centro

**Varianza.** La relación entre la media y la desviación móvil es débil
(correlación de 0.15) y el parámetro de Box-Cox (0.88) no se aproxima a
cero, por lo que no hay evidencia fuerte de que la transformación
logarítmica sea estrictamente necesaria. Aun así, el coeficiente de
variación crece de 0.24 en la primera mitad del entrenamiento a 0.46 en la
segunda, sobre todo por la ruptura de 2020. Se aplicó **`log(1+x)`** como
decisión conservadora de modelado, no porque la varianza lo exigiera de
forma estricta.

**Media.** La prueba ADF sobre el log-nivel produjo un valor p de 0.20, sin
rechazar la raíz unitaria; la ACF confirma persistencia (0.88 en el rezago 1
y 0.35 en el rezago 6). Una diferencia regular basta para reducir el valor p
a 0.04, y se añadió además una diferencia estacional para eliminar el
patrón anual: **d = 1, D = 1**.

### 4.6 Región América del Norte

**Varianza.** La correlación entre media y desviación móvil es negativa
(−0.34) y el Box-Cox (1.53) tampoco se acerca a cero; la evidencia de
varianza no constante es débil. El coeficiente de variación también crece
en la segunda mitad del entrenamiento (0.22 → 0.45). Se aplicó la misma
transformación conservadora, **`log(1+x)`**.

**Media.** La prueba ADF en nivel rechaza la raíz unitaria (p = 0.01), pero
deja de hacerlo tras aplicar el logaritmo (p = 0.16), por lo que la
diferenciación se estudió sobre la escala transformada. La primera
diferencia queda al límite de significancia (p ≈ 0.05); combinada con una
diferencia estacional, rechaza claramente la raíz unitaria: **d = 1, D = 1**.

### 4.7 Región Europa

**Varianza.** La correlación media–desviación es −0.23 y el Box-Cox (1.68)
tampoco se aproxima a cero. El coeficiente de variación crece de 0.23 a
0.49 entre ambas mitades del entrenamiento. Se aplicó igualmente
**`log(1+x)`** como decisión conservadora.

**Media.** El valor p de ADF en log-nivel es 0.28; una primera diferencia
regular todavía deja un valor p de 0.11, insuficiente. La diferencia
estacional de doce meses sí produce un valor p menor a 0.001, por lo que
Europa necesita **D = 1** pero no una diferencia regular adicional
(**d = 0**) — la única de las siete series que no requiere diferenciación
regular.

![Estabilidad de la varianza antes y después de log1p — las tres regiones](img/region_figura_5_varianza_transformacion.png)

![ACF en nivel y ACF/PACF transformadas — las tres regiones](img/region_figura_6_acf_pacf.png)

*Nota metodológica:* a diferencia de las vías, en las regiones la evidencia
de no-estacionariedad en varianza (correlación media–desviación, Box-Cox)
resultó débil en las tres; el uso de `log(1+x)` se mantuvo como decisión
conservadora de modelado y no como una transformación estrictamente exigida
por los datos.

---

## 5. Generación de modelos

Para cada serie se identifican p, d, q a partir de la ACF y la PACF, se
explican los modelos elegidos (incluidos los propuestos automáticamente), se
generan los cuatro algoritmos solicitados y se comparan por residuos,
métricas de error, AIC y BIC.

### 5.1 Serie total internacional

**Identificación de p, d, q vía ACF y PACF.** Sobre la serie ya transformada
(log1p + diferencia estacional), ni la ACF ni la PACF muestran rezagos
significativos en el corto plazo (1 a 6), por lo que la parte no estacional
queda vacía: **p = 0, q = 0**. El único rezago relevante es el 12, presente
en ambas funciones; como la ACF corta en seco en el rezago 24 mientras la
PACF decae de forma gradual, la regla de Box-Jenkins identifica un
componente de medias móviles estacional: **P = 0, Q = 1**. Con **D = 1** y
d = 0, el modelo resultante es un **SARIMA(0,0,0)(0,1,1)₁₂ con constante**,
llamado M1 en el notebook.

![ACF y PACF de la serie transformada — Total internacional](img/total_cell56_0.png)

![ACF y PACF de la serie transformada — Total internacional](img/total_cell59_0.png)

**Explicación de la elección de parámetros, incluidos los automáticos.**
Además de M1, se ajustó una malla automática de 36 combinaciones de órdenes
alrededor de esa propuesta y un modelo "airline" (0,1,1)(0,1,1)₁₂ clásico
(M3), para contrastar la lectura manual contra una búsqueda exhaustiva. La
malla confirma de forma independiente la parte estacional (0,1,1)₁₂ en los
cinco mejores órdenes; el mejor por AIC agrega dos términos autorregresivos
(M2, orden (2,0,0)(0,1,1)₁₂), con una mejora de apenas 4.9 puntos de AIC
sobre M1 — evidencia débil frente al costo de dos parámetros adicionales —,
por lo que por parsimonia se prefiere M1. También se comprobó que el ajuste
depende críticamente de la ventana de entrenamiento: sobre el entrenamiento
completo (que incluye el choque) ningún coeficiente estacional resulta
significativo, mientras que sobre la ventana pre-choque (2009-01 a 2020-02)
los tres coeficientes de M1 son significativos (p < 0.001).

**Modelos generados con los distintos algoritmos.** Se generaron seasonal
naive (línea base), suavizamiento exponencial simple y Holt-Winters (aditivo
y amortiguado), cada uno sobre la ventana de entrenamiento completa y sobre
la ventana pre-choque. *Nota:* Prophet no estaba disponible en el entorno de
ejecución; como el enunciado admite cualquiera de las alternativas, se
implementaron en su lugar las tres restantes.

![Pronósticos de los modelos alternativos por ventana — Total internacional](img/total_cell72_0.png)

**Comparación por residuos, métricas de error, AIC y BIC.** Los residuos de
los tres SARIMA sobre la ventana completa fallan la prueba de
heterocedasticidad y muestran curtosis muy por encima de lo esperado en una
distribución normal; sobre la ventana pre-choque los tres pasan Ljung-Box, la
heterocedasticidad ya no se rechaza y la curtosis baja a un rango razonable.
El AIC y el BIC solo se compararon dentro de la familia SARIMA: AIC prefiere
a M2 y BIC a M3, con M1 muy cerca de ambos; las diferencias son pequeñas y no
discriminan de forma concluyente dentro de la muestra. Frente a Holt-Winters
y seasonal naive, la comparación se hizo exclusivamente con métricas de
error sobre el conjunto de prueba, no con AIC/BIC.

![Diagnóstico de residuos por ventana — Total internacional](img/total_cell69_0.png)

![Diagnóstico de residuos por ventana — Total internacional](img/total_cell69_1.png)

### 5.2 Serie Aérea

La función de autocorrelación parcial sugirió **p = 2**, mientras que la
función de autocorrelación sugirió **q = 2**, sobre la serie diferenciada
(d = 1). A partir de estos resultados se compararon diferentes modelos
ARIMA y SARIMA cercanos. El mejor candidato de esta familia fue:

**SARIMA (0,1,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 2,869.86, un BIC de 2,884.24 y un valor p de
Ljung-Box de 0.65 en entrenamiento, lo que indica que sus residuos no
conservaron autocorrelación significativa dentro del conjunto usado para
ajustarlo.

También se generaron los modelos Prophet, Holt-Winters, suavizamiento
exponencial y Seasonal Naive. Los resultados sobre el conjunto de prueba
fueron:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Suavizamiento exponencial | 36,970.60 | 42,141.22 |
| Prophet | 41,271.36 | 45,655.27 |
| Holt-Winters | 43,072.93 | 47,051.02 |
| Seasonal Naive | 75,512.73 | 79,339.80 |
| ARIMA/SARIMA | 74,524.43 | 79,593.05 |

El mejor resultado fue obtenido por **suavizamiento exponencial**, con los
menores valores de MAE y RMSE. Sin embargo, sus residuos de prueba
conservaron autocorrelación significativa, por lo que el modelo todavía dejó
patrones temporales sin explicar completamente.

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Aérea](img/aerea_diag_4.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Aérea](img/aerea_mod_1.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Aérea](img/aerea_mod_0.png)

### 5.3 Serie Terrestre

La PACF sugirió **p = 3**, mientras que la ACF sugirió **q = 2**. Después de
comparar diferentes combinaciones, el mejor modelo de la familia ARIMA/SARIMA
fue:

**SARIMA (0,1,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 3,091.31, un BIC de 3,105.69 y un valor p de
Ljung-Box de 0.55 en entrenamiento, por lo que sus residuos de entrenamiento
no mostraron autocorrelación significativa.

Los modelos comparados en prueba presentaron los siguientes resultados:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Prophet | 47,713.21 | 57,657.61 |
| Suavizamiento exponencial | 121,715.64 | 134,136.23 |
| Holt-Winters | 128,421.20 | 139,161.45 |
| Seasonal Naive | 132,209.04 | 144,274.98 |
| ARIMA/SARIMA | 147,398.53 | 158,502.92 |

El mejor modelo fue **Prophet**, con una diferencia amplia respecto de los
demás algoritmos. Este resultado sugiere que su capacidad para representar
cambios de tendencia fue más adecuada para una serie afectada por el choque
de 2020 y la recuperación posterior. A pesar de obtener los menores errores,
sus residuos de prueba conservaron autocorrelación significativa.

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Terrestre](img/terrestre_diag_4.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Terrestre](img/terrestre_mod_1.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Terrestre](img/terrestre_mod_0.png)

### 5.4 Serie Marítima

La PACF sugirió **p = 3** y la ACF sugirió **q = 2**. El mejor candidato
ARIMA/SARIMA fue:

**SARIMA (0,2,2)(1,0,1,12)**

Este modelo obtuvo un AIC de 551.92, un BIC de 566.26 y un valor p de
Ljung-Box de 0.07 en entrenamiento. Entre los candidatos evaluados, fue uno
de los que combinó valores bajos de AIC y BIC con residuos sin autocorrelación
significativa al nivel de 5%.

Los resultados de prueba fueron:

| Modelo | MAE | RMSE |
|---|---:|---:|
| Holt-Winters | 902.62 | 1,685.06 |
| Suavizamiento exponencial | 858.37 | 1,731.93 |
| Seasonal Naive | 858.37 | 1,731.93 |
| ARIMA/SARIMA | 858.37 | 1,731.93 |
| Prophet | 7,272.58 | 8,587.77 |

Aunque varios modelos obtuvieron un MAE ligeramente menor, **Holt-Winters**
presentó el menor RMSE, un sesgo relativamente bajo y residuos de prueba sin
autocorrelación significativa (Ljung-Box p = 0.19), por lo que fue
seleccionado como el modelo más adecuado para esta serie. Sus errores no
deben compararse directamente con los de Aérea y Terrestre, debido a la
diferencia de escala y a la limitación metodológica de su construcción.

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Marítima](img/maritima_diag_4.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Marítima](img/maritima_mod_1.png)

![Selección de p,d,q, modelo ARIMA y comparación de modelos — Serie Marítima](img/maritima_mod_0.png)

### 5.5 Región América del Centro

Se exploraron valores de p y q entre 0 y 2 sobre la serie diferenciada
(d = 1, D = 1). El modelo seleccionado fue:

**SARIMA(1,1,1)(1,1,0)[12]**

Obtuvo un AIC de 50.59, un BIC de 61.78 y un valor p de Ljung-Box de 0.84 en
el rezago 12, por lo que sus residuos no mostraron dependencia serial
significativa dentro del entrenamiento.

Se compararon cinco enfoques sobre el conjunto de prueba (ARIMA/SARIMA,
Prophet, Holt-Winters amortiguado, suavizamiento exponencial simple y
seasonal naive):

| Modelo | MAE | RMSE |
|---|---:|---:|
| Suavizamiento exponencial | 108,285 | 120,341 |
| Holt-Winters | 113,415 | 124,214 |
| Seasonal naïve | 134,400 | 144,899 |
| ARIMA/SARIMA | 150,584 | 163,920 |
| Prophet | 156,597 | 166,857 |

El mejor resultado en prueba fue el **suavizamiento exponencial simple**. El
entrenamiento termina cerca del punto más bajo de actividad, y los modelos
con tendencia y componentes más complejos —incluido el SARIMA seleccionado
por AIC/BIC— extrapolaron patrones que no representaron bien la reapertura
posterior.

### 5.6 Región América del Norte

Con la misma exploración de p y q entre 0 y 2, el modelo seleccionado fue:

**SARIMA(1,1,1)(1,1,0)[12]**

Obtuvo un AIC de 382.00, un BIC de 393.18 y un valor p de Ljung-Box de 0.75.
Sus diagnósticos dentro del entrenamiento fueron adecuados, pero al
proyectarlo sobre el conjunto de prueba produjo una **trayectoria
explosiva** — evidencia de que buenos diagnósticos dentro de la muestra no
garantizan estabilidad en un horizonte largo que atraviesa un cambio
estructural como la pandemia.

| Modelo | MAE | RMSE |
|---|---:|---:|
| Suavizamiento exponencial | 32,194 | 36,725 |
| Holt-Winters | 40,797 | 44,976 |
| Seasonal naïve | 49,974 | 53,533 |
| Prophet | 55,626 | 59,244 |
| ARIMA/SARIMA | 5.69 × 10²² | 2.63 × 10²³ |

El **suavizamiento exponencial simple** fue nuevamente el mejor modelo en
prueba, por la misma razón que en América del Centro: el corte de
entrenamiento coincide con el nivel más bajo de actividad.

### 5.7 Región Europa

Para Europa (d = 0, D = 1) se seleccionó:

**ARIMA(1,0,1)**

Obtuvo un AIC de 360.86, un BIC de 372.76 y un valor p de Ljung-Box de 0.87.
Algunos candidatos estacionales lograron un BIC menor, pero conservaron
autocorrelación residual significativa y fueron descartados por ese
criterio.

| Modelo | MAE | RMSE |
|---|---:|---:|
| ARIMA/SARIMA | 6,420 | 7,824 |
| Suavizamiento exponencial | 9,292 | 10,695 |
| Holt-Winters | 10,378 | 11,563 |
| Seasonal naïve | 11,076 | 12,135 |
| Prophet | 11,676 | 12,887 |

A diferencia de las otras dos regiones, aquí **ARIMA(1,0,1)** fue el mejor
modelo en prueba: capturó la dependencia de corto plazo sin producir la
inestabilidad observada en el SARIMA de América del Norte.

![Diagnóstico de residuos de los tres modelos regionales seleccionados](img/region_figura_7_residuos.png)

![Pronósticos sobre el conjunto de prueba — las tres regiones](img/region_figura_8_pronosticos.png)

*Nota:* en América del Norte la proyección SARIMA excede ampliamente la
escala de los datos; la figura anterior la recorta únicamente para
conservar la legibilidad, pero las métricas de la tabla se calcularon con
los valores completos, sin recortar.

### 5.8 Comparación de los modelos seleccionados

| Serie | Mejor modelo | MAE | RMSE | Autocorrelación en residuos de prueba |
|---|---|---:|---:|---|
| Total internacional | Holt-Winters amortiguado (ventana pre-choque) | 53,568.42 | 75,695.20 | No significativa |
| Aérea | Suavizamiento exponencial | 36,970.60 | 42,141.22 | Sí |
| Terrestre | Prophet | 47,713.21 | 57,657.61 | Sí |
| Marítima | Holt-Winters | 902.62 | 1,685.06 | No significativa |
| América del Centro | Suavizamiento exponencial | 108,285.00 | 120,341.00 | No reportada |
| América del Norte | Suavizamiento exponencial | 32,194.00 | 36,725.00 | No reportada |
| Europa | ARIMA(1,0,1) | 6,420.00 | 7,824.00 | No significativa (Ljung-Box p = 0.87 en entrenamiento) |

*Nota de comparabilidad:* ninguna de las tres familias de series (total,
vías, regiones) se evaluó con exactamente el mismo procedimiento. La serie
total descarta explícitamente todo modelo peor que su seasonal naive y
contrasta dos ventanas de entrenamiento; vías y regiones se ajustaron sobre
una única ventana de 147 meses, pero regiones no reporta la autocorrelación
de los residuos de prueba para los modelos de suavizamiento, solo el
Ljung-Box de entrenamiento de los candidatos ARIMA/SARIMA. Los RMSE de la
tabla no deben leerse como una carrera directa entre las siete series, sino
como el resumen de cuál algoritmo ganó en cada una.

El análisis demuestra que **no existe un único algoritmo que funcione mejor
para todas las series**: cada una necesitó un modelo diferente de acuerdo
con su tendencia, estacionalidad, variabilidad y presencia de cambios
estructurales. AIC y BIC se usaron principalmente para comparar candidatos
ARIMA/SARIMA y modelos de suavizamiento cuando estaban disponibles; Prophet
y Seasonal Naive se compararon sobre todo mediante los errores en el
conjunto de prueba y el comportamiento de los residuos. El caso de América
del Norte añade una advertencia adicional: ni el AIC ni el BIC ni el
Ljung-Box de entrenamiento anticiparon la inestabilidad de su SARIMA fuera
de muestra.

---

## 6. Predicción con los modelos generados

Los conjuntos de entrenamiento y prueba ya se describieron en la sección 2 y
son los mismos para las siete series. Aquí se resume qué tan bien predice
cada modelo seleccionado y cómo se comparan entre sí.

### 6.1 Serie total internacional

El desempeño depende casi por completo de la ventana de entrenamiento, más
que del algoritmo elegido: los modelos entrenados con toda la serie
(incluyendo el choque) quedan anclados en el piso pandémico y nunca alcanzan
el nivel real del conjunto de prueba; su mejor RMSE es 174,266. Los modelos
entrenados sobre la ventana pre-choque, en cambio, sí capturan el nivel y la
trayectoria correctos, con RMSE entre 75,695 y 81,574 entre los que superan
al seasonal naive. Vistos por sub-período, en 2021 (piso pandémico) los
modelos pre-choque fallan (MAPE superior al 290%), pero a partir de 2023 la
serie observada entra en la banda de confianza del 95% de estos modelos y no
vuelve a salir; para 2024-2026, ya con la serie normalizada, el mejor modelo
alcanza un MAPE de apenas 8.7%.

Sobre el conjunto de prueba, cualquier modelo entrenado en la ventana
completa resulta peor que el seasonal naive de esa misma ventana y se
descarta. El mejor resultado global es **Holt-Winters amortiguado sobre la
ventana pre-choque**, seguido muy de cerca por el SARIMA **M1
(0,0,0)(0,1,1)₁₂ con constante**, también sobre la ventana pre-choque, la
misma especificación identificada manualmente. Ambos reproducen con
precisión la forma del ciclo anual desde 2023 en adelante.

![Comparación de modelos y pronóstico final con intervalos de confianza — Total internacional](img/total_cell75_0.png)

![Comparación de modelos y pronóstico final con intervalos de confianza — Total internacional](img/total_cell75_1.png)

![Comparación de modelos y pronóstico final con intervalos de confianza — Total internacional](img/total_cell83_0.png)

![Comparación de modelos y pronóstico final con intervalos de confianza — Total internacional](img/total_cell83_1.png)

### 6.2 Series por vía de ingreso

Los modelos se ajustaron con las 147 observaciones de entrenamiento y se
evaluaron sobre 63 meses que no participaron en su estimación. La
comparación se realizó mediante MAE, RMSE, sesgo promedio y la prueba de
Ljung-Box aplicada a los residuos.

Para **Aérea**, el suavizamiento exponencial presentó el mejor desempeño de
prueba. Sin embargo, el RMSE de 42,141.22 representa un error relevante
frente a una media mensual de 90,568.66. Además, los residuos conservaron
autocorrelación, por lo que el modelo no capturó completamente la
recuperación posterior a la pandemia.

Para **Terrestre**, Prophet obtuvo el menor error, con un RMSE de 57,657.61.
Frente a una media mensual de 131,391.68, el error sigue siendo
considerable, pero fue claramente inferior al de los demás algoritmos. La
autocorrelación restante en los residuos indica que todavía quedaron
patrones por explicar.

Para **Marítima**, Holt-Winters obtuvo un RMSE de 1,685.06 frente a una
media mensual de 5,851.34. Sus residuos no conservaron autocorrelación
significativa, lo que indica que capturó de mejor forma la estructura
temporal disponible en el conjunto de prueba. Aun así, la predicción
marítima debe considerarse exploratoria debido a los cambios metodológicos
de la serie.

En general, los modelos permiten aproximar el comportamiento de los ingresos
migratorios, pero no deben utilizarse como predicciones exactas: la
pandemia produjo un quiebre estructural importante y el período de prueba
incluye una recuperación distinta del comportamiento observado en buena
parte del entrenamiento. Por ello, los pronósticos deben actualizarse
periódicamente con nueva información.

### 6.3 Series por región geográfica

Para **América del Centro** y **América del Norte**, el suavizamiento
exponencial simple fue el modelo con menor error en prueba. En ambos casos
el entrenamiento termina cerca del punto más bajo de actividad turística, y
los modelos con componentes de tendencia y estacionalidad más complejos
—incluidos los SARIMA seleccionados por AIC/BIC— extrapolaron patrones que
no representaron bien la reapertura posterior; en América del Norte esto
fue especialmente grave, con el SARIMA produciendo una proyección
explosiva y errores fuera de cualquier escala razonable.

Para **Europa**, en cambio, el mejor modelo fue el propio **ARIMA(1,0,1)**,
con un RMSE de 7,824 frente a los 10,695–12,887 de las alternativas.
Capturó la dependencia de corto plazo sin la inestabilidad del caso
norteamericano.

No existe un modelo universalmente superior para las tres regiones: el
mejor método depende de la escala, del comportamiento histórico y de la
forma en que cada región respondió a la ruptura de 2020. El caso de
América del Norte, en particular, demuestra que los diagnósticos de
residuos dentro del entrenamiento no bastan por sí solos: es indispensable
evaluar también el comportamiento del modelo fuera de muestra.

---

## 7. Análisis comparativo de las series

### 7.1 Vías de ingreso

| Serie | Fuerza estacional | Fuerza de tendencia | Coeficiente de variación | Pendiente mensual relativa antes de 2020 | Cambio 2020 frente a 2019 |
|---|---:|---:|---:|---:|---:|
| Aérea | 0.384 | 0.613 | 0.31 | 0.43% | −72.80% |
| Terrestre | 0.409 | 0.818 | 0.46 | 0.87% | −75.23% |
| Marítima | 0.641 | 0.576 | 1.15 | 0.44% | −67.89% |

*La serie total no se incluye en esta tabla porque su fuerza de tendencia y
estacionalidad se calcularon con una metodología distinta (por ventana,
antes y después de excluir el choque — ver sección 3.1); no son
directamente comparables punto a punto con estos valores.*

**¿Cuál vía presenta mayor estacionalidad?** La vía **Marítima** presentó la
mayor fuerza estacional, con un valor de 0.641. Esto indica que su flujo
depende en mayor medida del mes del año. Aérea y Terrestre también
presentaron patrones estacionales, pero con menor intensidad.

**¿Cuál vía presenta mayor tendencia de crecimiento?** La vía **Terrestre**
presentó la tendencia más fuerte, con un valor de 0.818, y la mayor
pendiente mensual relativa antes de la pandemia (≈0.87%). Aérea presentó una
pendiente relativa de 0.43% y Marítima de 0.44%.

**¿Cuál vía presenta mayor volatilidad?** La vía **Marítima** presentó la
mayor volatilidad relativa, con un coeficiente de variación de 1.15,
considerablemente superior al de Terrestre (0.46) y Aérea (0.31). La
elevada dispersión marítima puede estar relacionada tanto con la naturaleza
de este flujo como con los cambios metodológicos documentados.

**¿Cuál vía fue más afectada por la pandemia?** La vía **Terrestre**
presentó la mayor caída entre 2019 y 2020, con una reducción de 75.23%. La
vía Aérea disminuyó 72.80% y Marítima 67.89%. Estos resultados muestran que
las restricciones de movilidad afectaron especialmente los ingresos por
fronteras terrestres.

**Comparación general.** Aérea fue la serie menos volátil y presentó un
comportamiento relativamente más estable. Terrestre mostró el mayor
crecimiento previo a la pandemia, pero también la caída porcentual más
fuerte en 2020. Marítima presentó la mayor estacionalidad y volatilidad,
además de cambios de clasificación que reducen su comparabilidad directa. La
serie total, al ser una agregación de las vías bajo el criterio
Turista/Excursionista (que excluye la reconstrucción especial de Marítima),
refleja sobre todo la dinámica combinada de Aérea y Terrestre: por eso su
fuerza de tendencia (0.80 sobre el entrenamiento completo) es casi tan alta
como la de Terrestre (0.818), la más alta de las cuatro series.

### 7.2 Regiones geográficas

Para evitar que la pandemia distorsione las características estructurales,
estas comparaciones se calcularon sobre el período enero 2009 – diciembre
2019 (excluyendo el choque), y el impacto y la recuperación se midieron
comparando 2020 y 2024 contra 2019.

| Región | Fuerza estacional pre-2020 | Crecimiento anual compuesto 2009-2019 | Volatilidad interanual pre-2020 | Impacto 2020 vs. 2019 | Recuperación 2024 vs. 2019 |
|---|---:|---:|---:|---:|---:|
| América del Centro | 0.69 | 9.83% | 14.49% | −74.43% | −34.87% |
| América del Norte | 0.89 | 3.81% | 11.98% | −74.14% | +33.56% |
| Europa | 0.88 | 2.33% | 12.74% | −71.83% | +17.98% |

**¿Cuál región presenta mayor estacionalidad?** **América del Norte**, con
0.89, muy cerca de Europa (0.88). América del Centro queda más atrás, con
0.69. Estos valores difieren de los reportados en la sección 3 porque aquí
se excluye la ruptura de 2020, que distorsiona el patrón estacional normal.

**¿Cuál región presenta mayor tendencia de crecimiento?** **América del
Centro**, con un crecimiento anual compuesto de 9.83% entre 2009 y 2019,
muy por encima de América del Norte (3.81%) y Europa (2.33%).

**¿Cuál región presenta mayor volatilidad?** **América del Centro**
también, con una volatilidad interanual de 14.49% frente a 12.74% en
Europa y 11.98% en América del Norte: el crecimiento más acelerado vino
acompañado de variaciones relativas más amplias.

**¿Cuál región fue más afectada por la pandemia?** Las tres cayeron de
forma similar en 2020 (entre −71.83% y −74.43%), lo que confirma que el
choque fue generalizado y no específico de una región. La diferencia
aparece en la recuperación: para 2024, América del Norte y Europa ya
superaban su nivel de 2019 (+33.56% y +17.98%), mientras que América del
Centro seguía 34.87% por debajo — la única de las tres regiones que no
había recuperado su nivel prepandemia.

**Comparación general.** América del Centro combina el mayor crecimiento
histórico con la mayor volatilidad y la recuperación más débil frente a
2019; América del Norte y Europa crecieron con más moderación pero se
recuperaron con más solidez. Esto contrasta con el patrón de las vías: allí
Terrestre —el canal dominante de América del Centro— fue también el más
golpeado por la pandemia (sección 7.1), reforzando la misma lectura desde
dos ángulos distintos de la serie.

---

## 8. Descubrimientos útiles para INGUAT

1. **Diciembre concentra el mayor flujo promedio en las tres vías de
   ingreso.** Este patrón puede utilizarse para anticipar una mayor demanda
   de personal, información turística, transporte y atención en los puntos
   de ingreso durante ese mes.

2. **La vía Terrestre concentra el 59.07% del volumen acumulado (27.6
   millones de visitantes) y tuvo el mayor crecimiento estructural antes de
   la pandemia**, con la pendiente mensual relativa más alta de las tres
   vías (0.87%). Es el canal prioritario para inversión en infraestructura
   fronteriza — La Aurora, Valle Nuevo, San Cristóbal, Pedro de Alvarado y
   La Ermita concentran juntas más del 80% del acumulado por frontera — y
   para acciones dirigidas a visitantes regionales.

3. **Terrestre fue también la vía más golpeada por la pandemia** (−75.23%
   en 2020), y América del Centro —que ingresa 73.8% de sus visitantes por
   tierra— es, de las tres regiones, la única que en 2024 seguía 34.87%
   por debajo de su nivel de 2019. La recuperación del mercado
   centroamericano por la vía terrestre debería ser una prioridad de
   promoción y facilitación fronteriza.

4. **Aérea presenta la menor volatilidad relativa** (coeficiente de
   variación de 0.31). Su comportamiento más estable permite planificar
   capacidad aeroportuaria y coordinar con aerolíneas con mayor certeza que
   en Terrestre o Marítima.

5. **Marítima requiere una revisión de calidad y consistencia de datos.**
   Los cambios en la clasificación de viajeros desde 2017 dificultan la
   comparación histórica. Mantener definiciones homogéneas y documentar
   claramente cualquier cambio en las categorías mejoraría la
   confiabilidad de futuras decisiones basadas en esta vía.

6. **La conectividad debe planificarse por región de origen.** América del
   Centro depende principalmente de accesos terrestres, mientras que
   América del Norte (80.0% aérea) y Europa (64.2% aérea) dependen
   sobre todo de la conectividad aérea; la inversión en infraestructura
   fronteriza y las alianzas con aerolíneas deben diferenciarse según el
   mercado de origen.

7. **La recuperación debe compararse contra el nivel de 2019, no solo
   contra el fondo de la pandemia.** Con ese criterio, América del Norte
   (+33.56%) y Europa (+17.98%) ya habían superado su nivel prepandemia en
   2024, mientras que América del Centro (−34.87%) no — un argumento para
   concentrar esfuerzos de recuperación y promoción en el mercado
   centroamericano.

8. **América del Centro combina el mayor crecimiento histórico con la
   mayor volatilidad de las tres regiones** (9.83% de crecimiento anual
   compuesto entre 2009 y 2019, frente a una volatilidad interanual de
   14.49%). Es el mercado de mayor potencial, pero también el que más
   exige monitoreo cercano y estrategias de contingencia ante variaciones
   bruscas.

9. **Estados Unidos (14.91% del acumulado) y Honduras (5.40%) son, después
   de El Salvador y de los residentes guatemaltecos, los orígenes de mayor
   volumen.** Junto con la fuerte dependencia aérea de América del Norte,
   esto refuerza a Estados Unidos como mercado prioritario para mantener y
   ampliar rutas y frecuencias aéreas.

10. **Las proyecciones deben tratarse como rangos de planificación, no
    como cifras exactas, y actualizarse con cada nuevo mes de datos
    disponible.** La pandemia produjo un quiebre estructural cuya
    recuperación todavía está en curso y difiere en ritmo por vía y por
    región, por lo que cualquier pronóstico usado para planificar debe
    revisarse conforme se incorpore información reciente.

---

## 9. Conclusiones generales

Las siete series analizadas comparten un mismo patrón de fondo —crecimiento
antes de 2020, colapso durante la pandemia y recuperación posterior— pero
difieren en la intensidad de su estacionalidad, su tendencia, su
volatilidad y en qué tan completa fue esa recuperación, y requirieron
tratamientos estadísticos específicos. Aérea mostró una estacionalidad
moderada, una tendencia importante y la menor volatilidad relativa.
Terrestre presentó la tendencia de crecimiento más fuerte de las cuatro
series nacionales (0.818) y el mayor impacto de la pandemia. Marítima fue
la más estacional y volátil de las vías, con resultados condicionados por
cambios metodológicos en la clasificación de los viajeros. La serie total,
que agrega Aérea y Terrestre bajo el criterio de comparabilidad, presentó
una tendencia casi tan dominante como la de Terrestre (0.80 frente a
0.818). Entre las regiones, América del
Centro combinó el mayor crecimiento histórico con la mayor volatilidad y la
recuperación más débil frente a 2019, mientras que América del Norte y
Europa, con crecimientos más moderados, ya habían superado su nivel de 2019
en 2024.

Las transformaciones y diferenciaciones permitieron alcanzar estacionariedad
antes de ajustar los modelos: Aérea y Terrestre no necesitaron transformación
logarítmica y alcanzaron estacionariedad con una diferencia regular; Total y
Marítima sí necesitaron `log1p`, con una diferencia estacional en el caso de
Total y dos diferencias regulares en el caso de Marítima, la que requirió
mayor grado de diferenciación de las cuatro.

Los parámetros ARIMA/SARIMA fueron propuestos mediante ACF, PACF y pruebas
de estacionariedad, y posteriormente se compararon diferentes candidatos con
AIC, BIC y diagnóstico de residuos. Además, se evaluaron variantes de
Holt-Winters, suavizamiento exponencial y Seasonal Naive bajo el mismo
conjunto de prueba en las siete series, y Prophet en las seis series de
vías y regiones (no disponible en el entorno usado para la serie total).

El mejor modelo fue distinto para cada serie: suavizamiento exponencial para
Aérea, Prophet para Terrestre, Holt-Winters para Marítima, Holt-Winters
amortiguado —entrenado sobre la ventana previa al choque sanitario— para la
serie total (con el SARIMA M1(0,0,0)(0,1,1)₁₂+c como alternativa casi
equivalente), suavizamiento exponencial para América del Centro y América
del Norte, y ARIMA(1,0,1) para Europa. Los resultados confirman que la
selección de algoritmo debe hacerse según las características de cada
serie y no de forma genérica. La autocorrelación presente en los residuos
de Aérea y Terrestre indica que sus predicciones todavía pueden mejorarse,
mientras que Marítima y Total sí alcanzaron residuos de prueba sin
autocorrelación significativa; el caso de América del Norte, cuyo SARIMA
pasó los diagnósticos de entrenamiento pero produjo un pronóstico
explosivo, añade una advertencia adicional sobre la necesidad de validar
siempre fuera de muestra.

Finalmente, los modelos pueden apoyar la planificación de INGUAT,
especialmente para anticipar meses de mayor flujo, identificar vías y
regiones con crecimiento importante, y evaluar la sensibilidad ante choques
externos. Su uso debe complementarse con actualizaciones frecuentes, con
una mejora en la consistencia del registro marítimo, con el seguimiento de
la recuperación regional frente a los niveles de 2019, y con la lección más
general de este análisis: ante un choque estructural como la pandemia,
conviene contrastar explícitamente modelos entrenados antes y después del
evento, y validar siempre el desempeño fuera de muestra, en vez de asumir
que un buen ajuste dentro del entrenamiento —o usar toda la información
disponible— es siempre la mejor opción.

---

## Anexo. Candidatos ARIMA y SARIMA evaluados por región

Se muestran los candidatos comparados para cada región antes de seleccionar
el modelo final (sección 5.5–5.7). La selección no se basó únicamente en el
menor BIC: también se exigió que los residuos no conservaran autocorrelación
significativa, lo que explica por qué algunos modelos con BIC menor fueron
descartados. Todos los candidatos listados convergieron correctamente.

**Tabla A1. Candidatos para América del Centro**

| Modelo | AIC | BIC | p de Ljung-Box |
|---|---:|---:|---:|
| SARIMA(1,1,1)(1,1,0)[12] | 50.59 | 61.78 | 0.84 |
| SARIMA(0,1,1)(0,1,1)[12] | 58.69 | 67.05 | <0.01 |
| SARIMA(1,1,1)(0,1,1)[12] | 60.62 | 71.77 | <0.01 |
| SARIMA(2,1,1)(0,1,1)[12] | 61.79 | 75.73 | <0.01 |
| SARIMA(1,1,2)(0,1,1)[12] | 63.08 | 76.97 | <0.01 |
| ARIMA(0,1,1) | 83.48 | 89.42 | 1.00 |
| ARIMA(1,1,0) | 83.82 | 89.78 | 1.00 |
| ARIMA(1,1,1) | 84.89 | 93.79 | 0.98 |
| ARIMA(2,1,1) | 83.40 | 95.28 | 0.98 |

**Tabla A2. Candidatos para América del Norte**

| Modelo | AIC | BIC | p de Ljung-Box |
|---|---:|---:|---:|
| SARIMA(1,1,2)(0,1,1)[12] | 373.44 | 387.33 | 0.01 |
| SARIMA(0,1,1)(0,1,1)[12] | 381.90 | 390.26 | 0.04 |
| SARIMA(2,1,1)(0,1,1)[12] | 377.16 | 391.10 | 0.01 |
| SARIMA(1,1,1)(1,1,0)[12] | 382.00 | 393.18 | 0.75 |
| SARIMA(1,1,1)(0,1,1)[12] | 383.44 | 394.59 | 0.02 |
| ARIMA(0,1,1) | 433.63 | 439.57 | 0.44 |
| ARIMA(1,1,0) | 435.59 | 441.55 | 0.45 |
| ARIMA(1,1,1) | 435.41 | 444.32 | 0.35 |
| ARIMA(2,1,1) | 433.05 | 444.93 | 0.18 |

**Tabla A3. Candidatos para Europa**

| Modelo | AIC | BIC | p de Ljung-Box |
|---|---:|---:|---:|
| SARIMA(1,0,1)(0,1,1)[12] | 313.84 | 325.02 | <0.01 |
| SARIMA(1,0,1)(1,1,0)[12] | 315.61 | 326.83 | <0.01 |
| SARIMA(2,0,1)(0,1,1)[12] | 313.18 | 327.16 | 0.02 |
| SARIMA(1,0,2)(0,1,1)[12] | 313.64 | 327.58 | <0.01 |
| ARIMA(1,0,1) | 360.86 | 372.76 | 0.87 |
| ARIMA(2,0,1) | 359.80 | 374.68 | 0.20 |
| ARIMA(1,0,0) | 366.63 | 375.58 | 0.71 |
| SARIMA(0,0,1)(0,1,1)[12] | 418.43 | 426.81 | <0.01 |
| ARIMA(0,0,1) | 471.67 | 480.60 | <0.01 |

---

## Respuestas

> ### a. Para cada categoría seleccionada
>
> #### Serie total de visitantes internacionales
>
> *Esta categoría tiene una sola serie (la suma de todas las vías, sin la
> etiqueta "Guatemala"), así que las cuatro preguntas se responden con sus
> propios valores en vez de comparar contra otras series de la misma
> categoría.*
>
> - **i. Estacionalidad:** sí presenta, con una fuerza estacional de
>   **0.46** sobre el entrenamiento completo, que sube a **0.73** al
>   excluir el choque de 2020 — un nivel similar al de la vía Marítima y
>   por debajo del de América del Norte y Europa (~0.88–0.89).
>   *(sección 3.1)*
> - **ii. Tendencia de crecimiento:** sí presenta, con una fuerza de
>   **0.80** sobre el entrenamiento completo (0.88 al excluir el choque),
>   equivalente a un crecimiento interanual de ≈7%. Es un valor cercano al
>   más alto de las otras dos categorías (Terrestre 0.818, Europa 0.81),
>   aunque no son estrictamente comparables punto a punto: Total usa una
>   ventana pre-choque especial y vías/regiones no. *(sección 3.1)*
> - **iii. Volatilidad:** coeficiente de variación de **0.47**
>   (desviación estándar 74,176 / media 156,388, sobre 2009–2026), un nivel
>   intermedio entre Terrestre (0.46) y Marítima (1.15). *(sección 1)*
> - **iv. Impacto de la pandemia:** la caída más profunda de las tres
>   categorías — el índice 2019 = 100 baja a **22.73 en 2020** (−77.3%,
>   frente a −75.23% de Terrestre y −74.43% de América del Centro, las
>   caídas mayores de las otras dos categorías). La recuperación observada
>   también es la más sólida de las que sí reportan un índice comparable:
>   en 2024 ya llega a **134.82** (+34.8% sobre 2019) y en 2025 sube a
>   138.02, por encima de América del Norte (+33.56%) y Europa (+17.98%);
>   las vías no reportan un índice de recuperación equivalente. El mejor
>   modelo (Holt-Winters amortiguado entrenado antes del choque) reproduce
>   esta trayectoria con un error de apenas 8.7% (MAPE) en 2024-2026.
>   *(secciones 1.1 y 6.1)*
>
> #### Vías de ingreso
>
> - **i. ¿Cuál presenta mayor estacionalidad?** **Marítima**, con una fuerza
>   estacional de **0.641** (Aérea 0.384, Terrestre 0.409). *(sección 7.1)*
> - **ii. ¿Cuál presenta mayor tendencia de crecimiento?** **Terrestre**,
>   con una fuerza de tendencia de **0.818** y la mayor pendiente mensual
>   relativa antes de 2020 (≈0.87%). *(sección 7.1)*
> - **iii. ¿Cuál presenta mayor volatilidad?** **Marítima**, con un
>   coeficiente de variación de **1.15**, muy por encima de Terrestre (0.46)
>   y Aérea (0.31). *(sección 7.1)*
> - **iv. ¿Cuál fue la más afectada por la pandemia?** **Terrestre**, con
>   una caída de **75.23%** entre 2019 y 2020 (Aérea −72.80%, Marítima
>   −67.89%). *(sección 7.1)*
>
> #### Regiones geográficas
>
> - **i. ¿Cuál presenta mayor estacionalidad?** **América del Norte**, con
>   una fuerza estacional pre-2020 de **0.89**, muy cerca de Europa (0.88);
>   América del Centro queda más atrás (0.69). *(sección 7.2)*
> - **ii. ¿Cuál presenta mayor tendencia de crecimiento?** **América del
>   Centro**, con un crecimiento anual compuesto de **9.83%** entre 2009 y
>   2019, muy por encima de América del Norte (3.81%) y Europa (2.33%).
>   *(sección 7.2)*
> - **iii. ¿Cuál presenta mayor volatilidad?** **América del Centro**
>   también, con una volatilidad interanual pre-2020 de **14.49%**, frente a
>   12.74% en Europa y 11.98% en América del Norte. *(sección 7.2)*
> - **iv. ¿Cuál fue la más afectada por la pandemia?** Las tres cayeron de
>   forma muy similar en 2020 (entre −71.83% y −74.43%), lo que confirma un
>   choque generalizado más que regional; en términos estrictos la más
>   golpeada fue **América del Centro** (−74.43%). La diferencia real
>   aparece en la recuperación: para 2024 América del Norte (+33.56%) y
>   Europa (+17.98%) ya habían superado su nivel de 2019, mientras que
>   **América del Centro seguía 34.87% por debajo** — la única de las tres
>   que aún no se recuperaba. *(sección 7.2)*
>
> ### b. En general
>
> **i. ¿Qué descubrimientos serían más útiles para que INGUAT tome
> decisiones?** *(lista completa de 10 hallazgos en la sección 8; los más
> accionables son)*
>
> 1. **Terrestre concentra el mayor volumen, el mayor crecimiento
>    estructural y también el mayor impacto de la pandemia**, con América
>    del Centro —que ingresa mayoritariamente por esa vía— todavía por
>    debajo de su nivel de 2019 en 2024. Es el canal y el mercado
>    prioritarios para inversión en infraestructura fronteriza y
>    estrategias de recuperación.
> 2. **La conectividad y la planificación de recursos deben diferenciarse
>    por canal y por región de origen.** Terrestre/América del Centro y
>    Aérea/América del Norte y Europa son, en la práctica, los mismos dos
>    patrones de acceso vistos desde ángulos distintos (sección 0.6), y
>    diciembre es sistemáticamente el mes de mayor flujo en las tres vías.
> 3. **La recuperación debe medirse contra el nivel de 2019, no solo contra
>    el fondo de la pandemia.** Con ese criterio, América del Norte y
>    Europa ya se habían recuperado en 2024 y América del Centro no, pese a
>    haber tenido el mayor crecimiento histórico y ser el mercado más
>    volátil.
> 4. **La vía Marítima y, en general, cualquier serie con cambios de
>    definición, requieren mejorar la consistencia del registro** antes de
>    poder usarse con la misma confianza que Aérea o Terrestre para la toma
>    de decisiones.
> 5. **Aérea, por su menor volatilidad, permite una planificación de
>    capacidad más predecible** que Terrestre o Marítima, lo que la hace un
>    canal atractivo para fortalecer con nuevas rutas y alianzas con
>    aerolíneas, particularmente hacia Estados Unidos, el segundo país de
>    origen en volumen.
> 6. **Las proyecciones deben tratarse como rangos de planificación y
>    actualizarse con cada nuevo mes de datos**, dado que la recuperación
>    posterior a 2020 todavía está en curso y su ritmo difiere por vía y
>    por región.
