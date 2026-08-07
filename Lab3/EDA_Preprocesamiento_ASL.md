# Análisis exploratorio y preparación del conjunto ASL Alphabet

## Introducción

El reconocimiento automático del alfabeto de la lengua de señas estadounidense constituye un problema de clasificación de imágenes en el que pequeñas diferencias visuales pueden cambiar por completo el significado de una seña. A diferencia de conjuntos como MNIST, cuyas observaciones son imágenes simples y estandarizadas, ASL Alphabet contiene fotografías reales de manos. En consecuencia, además de la forma de los dedos, intervienen factores como la iluminación, el fondo, la posición de la mano, la escala y la nitidez. Antes de entrenar un modelo era necesario comprender estas características, identificar posibles dificultades y establecer un procedimiento reproducible para preparar los datos.

En esta etapa se realizó el análisis exploratorio del conjunto ASL Alphabet de Kaggle. El trabajo incluyó la revisión de la estructura y calidad de los archivos, la visualización de diferentes letras, el estudio de la variabilidad dentro de cada clase, la identificación de señas visualmente similares, la creación de conjuntos propios de entrenamiento, validación y prueba, y la definición del preprocesamiento que se aplicará antes del entrenamiento. No se entrenó todavía una red neuronal, pues el propósito de esta fase fue construir una base metodológica clara y sustentada por los datos.

## Estructura y composición del conjunto de datos

El inventario completo confirmó la existencia de 87,000 imágenes de entrenamiento distribuidas en 29 clases. Veintiséis clases corresponden a las letras A–Z, mientras que `del`, `nothing` y `space` representan comandos o estados necesarios para una aplicación de escritura en tiempo real. Cada clase contiene exactamente 3,000 imágenes, equivalentes al 3.45 % del conjunto. La razón entre la clase de mayor tamaño y la de menor tamaño fue 1.000, por lo que el dataset se encuentra perfectamente balanceado en términos de cantidad.

Este balance es favorable porque evita que un futuro modelo encuentre más ejemplos de unas letras que de otras. Sin embargo, tener el mismo número de imágenes no garantiza que todas las clases presenten la misma dificultad. Algunas señas poseen diferencias muy evidentes, mientras que otras se distinguen únicamente por la posición de uno o dos dedos. Por esta razón, en etapas posteriores no será suficiente reportar una exactitud global: también deberán examinarse métricas individuales por clase y una matriz de confusión.

La inspección técnica de la submuestra confirmó que el 100 % de las imágenes analizadas estaba almacenado en formato JPEG, en modo RGB y con una resolución de 200 × 200 píxeles. No se encontraron archivos dañados entre las 17,400 imágenes procesadas. La homogeneidad de formato y dimensiones facilita la construcción de lotes, aunque el tamaño total continúa siendo considerable. Si las 87,000 fotografías se cargaran sin compresión como arreglos RGB de 200 × 200, requerirían aproximadamente 9.72 GiB, sin contar otras estructuras utilizadas durante el análisis o el entrenamiento.

El conjunto oficial de prueba contiene solamente 28 imágenes y no incluye la clase `del`. Por tanto, no resulta suficiente para medir de forma representativa el desempeño de un clasificador de 29 clases. Se conservó como un recurso adicional para comprobaciones cualitativas, pero no se utilizó como la prueba principal.

## Submuestra y exploración de la variabilidad visual

Debido al costo de procesar las 87,000 fotografías, se seleccionaron 600 imágenes por clase. La submuestra resultante contiene 17,400 observaciones, equivalentes al 20 % del dataset completo. Esta cantidad se encuentra dentro del rango recomendado de 500 a 800 imágenes por clase y conserva el balance original, ya que todas las etiquetas aportan exactamente el mismo número de ejemplos.

La exploración comenzó con una imagen de cada una de las 29 clases. Esta vista general permitió comprobar la relación entre carpetas y etiquetas, además de observar que las manos aparecen sobre fondos y condiciones de iluminación con cierto grado de variación. Posteriormente se estudiaron seis ejemplos de cada una de siete letras: A, M, N, S, U, V y R. En total, esta comparación específica reunió 42 fotografías y superó el requisito de mostrar al menos cinco letras distintas.

Las imágenes demostraron que una misma letra no ocupa siempre una posición idéntica. Se encontraron cambios de escala, rotación, encuadre, iluminación y apertura de los dedos. Esta variabilidad es importante porque un sistema útil debe reconocer la seña y no memorizar una ubicación exacta de la mano. Al mismo tiempo, las imágenes promedio por clase mostraron que existe una estructura espacial común: la silueta principal de cada gesto permanece visible, mientras que las regiones variables se vuelven más borrosas.

Como medida exploratoria, se calculó la distancia de cada imagen respecto de la imagen promedio de su clase. De acuerdo con esta aproximación, E, I y H fueron las letras con mayor variabilidad en la submuestra seleccionada. Este resultado no implica necesariamente que sean las clases más difíciles de clasificar. Una distancia alta puede originarse en cambios genuinos de postura, iluminación, fondo o encuadre. El hallazgo indica que estas clases deben revisarse con especial atención y que un futuro modelo necesitará tolerar variaciones razonables de captura.

## Similitud y posibles confusiones entre letras

La inspección visual permitió reconocer dos grupos particularmente importantes. Las letras M, N y S comparten la apariencia general de un puño cerrado. Sus diferencias se concentran en la ubicación del pulgar y en la forma en que los dedos lo cubren. Debido a que estas señales ocupan pocos píxeles, una resolución demasiado baja, una sombra o una ligera oclusión podría eliminar información decisiva.

Las letras U, V y R también presentan una estructura parecida porque utilizan principalmente dos dedos extendidos. En U los dedos permanecen juntos, en V aparecen separados y en R están cruzados. La orientación de la mano puede hacer que la separación o el cruce resulten menos evidentes, por lo que estas clases son candidatas naturales a confundirse.

Además de la observación manual, se compararon las imágenes promedio de las clases mediante similitud coseno. Los pares con mayor semejanza global fueron S–Y, U–W y K–V. Este análisis funciona como generador de hipótesis, no como evidencia definitiva de errores de clasificación. La similitud puede estar influida por la postura, la posición de la mano o incluso por elementos compartidos del fondo. Solo después de entrenar un modelo será posible comprobar cuáles pares se confunden realmente mediante una matriz de confusión.

Las variables globales también mostraron diferencias entre clases. Las medias de brillo abarcaron un rango de 32.5 niveles y las medias de contraste uno de 23.7 puntos. A pesar de esas diferencias, las distribuciones se solaparon ampliamente, por lo que brillo y contraste no bastan para separar las letras. Este resultado es conveniente: la señal principal debería encontrarse en la estructura espacial de la mano. No obstante, si algunas condiciones de captura están asociadas con etiquetas específicas, un modelo podría aprender atajos relacionados con el fondo o la iluminación. Por ello será importante evaluar posteriormente el sistema con personas y ambientes diferentes.

## Definición de entrenamiento, validación y prueba

La submuestra se dividió en 70 % para entrenamiento, 15 % para validación y 15 % para prueba. El conjunto de entrenamiento contiene 12,180 imágenes, es decir, 420 por clase. Validación y prueba contienen 2,610 imágenes cada uno, equivalentes a 90 ejemplos por clase. Los tres conjuntos conservan las 29 etiquetas y mantienen un balance exacto.

La división no se realizó asignando fotografías individuales de manera completamente independiente. Los nombres de los archivos poseen índices consecutivos y pueden corresponder a capturas realizadas en momentos cercanos. Una separación aleatoria podría colocar imágenes casi idénticas en entrenamiento y prueba, produciendo una estimación artificialmente optimista del rendimiento.

Para reducir este riesgo se agruparon las imágenes en bloques de 30 archivos consecutivos. Con una semilla fija de 42 se seleccionaron 20 bloques por clase: 14 se asignaron a entrenamiento, tres a validación y tres a prueba. Ningún bloque quedó presente en más de un conjunto y no se encontraron rutas repetidas entre las particiones. Esta estrategia mejora la independencia entre los datos, aunque no garantiza una separación completa por persona o sesión, ya que el dataset no proporciona identificadores de sujeto. Esta limitación deberá considerarse al interpretar los resultados del futuro modelo.

El conjunto de validación se utilizará para seleccionar configuraciones y vigilar el sobreajuste durante el entrenamiento. El conjunto de prueba permanecerá aislado y se consultará únicamente al terminar el desarrollo. Cualquier aumento artificial de imágenes deberá aplicarse después de esta división y exclusivamente sobre entrenamiento, evitando que versiones modificadas de una misma fotografía aparezcan en conjuntos diferentes.

## Preprocesamiento propuesto

El preprocesamiento definido conserva la información visual esencial y disminuye el costo computacional. Primero se corrige la orientación indicada por los metadatos EXIF, si existe, y cada fotografía se convierte explícitamente a RGB. Después se reduce su resolución de 200 × 200 a 64 × 64 mediante interpolación bilineal. Finalmente, el arreglo se transforma al tipo numérico `float32` y los valores de los píxeles se dividen entre 255 para ubicarlos en el intervalo de 0 a 1.

La prueba del procedimiento con cinco letras produjo un lote de forma 5 × 64 × 64 × 3. Las imágenes originales tenían tipo entero sin signo y valores entre 0 y 255. Después del preprocesamiento se obtuvieron valores de precisión flotante con un rango observado entre 0.0000 y 0.9922. El máximo no llegó exactamente a 1 en esos cinco ejemplos debido a la interpolación y a los valores particulares de las imágenes seleccionadas, pero el rango teórico permanece entre 0 y 1. Los tres canales RGB fueron conservados.

La reducción a 64 × 64 disminuye en 89.8 % la cantidad de valores por fotografía. Como referencia, la submuestra reducida requeriría aproximadamente 0.20 GiB si se almacenara como valores RGB de ocho bits, frente al costo mucho mayor del dataset completo en su resolución original. La comparación visual indicó que a 64 × 64 todavía se conservan la silueta de la mano y los espacios principales entre los dedos. Esta resolución representa un compromiso razonable para un laboratorio: reduce memoria y tiempo sin eliminar deliberadamente las características que separan las clases.

No se aplicaron filtros de desenfoque, enfoque artificial ni segmentación de fondo. Un filtro agresivo podría borrar precisamente las pequeñas separaciones entre dedos que distinguen M de N o U de V. Tampoco se modificaron permanentemente los archivos originales; todas las transformaciones se realizan al cargar las imágenes, lo que permite ajustar el procedimiento en el futuro sin perder información.

Como estrategia posterior podrían incorporarse aumentos moderados de rotación, traslación, zoom e iluminación. Estos cambios deben mantenerse dentro de condiciones realistas y aplicarse únicamente durante el entrenamiento. Validación y prueba recibirán solo las transformaciones deterministas: corrección de orientación, conversión a RGB, reducción de tamaño y normalización.

## Conclusiones

El análisis confirmó que ASL Alphabet es un conjunto amplio, técnicamente uniforme y balanceado, pero no necesariamente sencillo. Sus 29 clases contienen la misma cantidad de imágenes, aunque algunas letras se diferencian por detalles pequeños y presentan niveles distintos de variabilidad. La observación de varias fotografías por letra permitió identificar cambios naturales dentro de una clase y anticipar confusiones en grupos como M/N/S y U/V/R. Las comparaciones cuantitativas aportaron otros pares de interés, pero estos deberán validarse después con los errores reales del clasificador.

La submuestra de 600 imágenes por clase y la reducción a 64 × 64 hacen viable el trabajo dentro de los límites del laboratorio. La división por bloques establece una prueba más rigurosa que una separación puramente aleatoria, mientras que la normalización proporciona entradas consistentes para una futura red neuronal. En conjunto, esta etapa no se limitó a describir las imágenes: definió decisiones reproducibles, documentó sus razones y señaló los riesgos que deberán considerarse al interpretar el rendimiento del sistema.

El siguiente paso será entrenar un modelo utilizando únicamente el conjunto de entrenamiento, tomar decisiones con validación y reservar la prueba para una evaluación final. Los resultados deberán analizarse por clase, prestando especial atención a las letras visualmente similares y a la capacidad de generalizar hacia manos, fondos e iluminación que no estén representados en los datos de desarrollo.

## Referencia

Grassknoted. *ASL Alphabet*. Kaggle: https://www.kaggle.com/datasets/grassknoted/asl-alphabet
