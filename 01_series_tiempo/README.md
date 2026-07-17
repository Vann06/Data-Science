# 01 · Series de tiempo — Temperatura de Guatemala

Proyecto de análisis y predicción de la temperatura promedio mensual de Guatemala entre enero de 1950 y junio de 2026.

## Objetivo

Explorar el comportamiento de la temperatura a través del tiempo, determinar si presenta tendencia y estacionalidad, verificar su estacionariedad y construir modelos capaces de predecir valores mensuales recientes.

## Preguntas desarrolladas

1. ¿Cuáles son los valores mínimos, máximos y promedios de temperatura?
2. ¿Cómo cambian los extremos según la profundidad de las capas del suelo?
3. ¿La temperatura ha aumentado, disminuido o se ha mantenido constante?
4. ¿La serie presenta tendencia y estacionalidad?
5. ¿Es estacionaria en media y en varianza?
6. ¿Qué parámetros sugieren las funciones ACF y PACF?
7. ¿Qué modelo SARIMA presenta el mejor desempeño?
8. ¿Cómo se compara SARIMA con Holt-Winters, suavizamiento exponencial y naive estacional?
9. ¿El modelo puede utilizarse para pronosticar valores promedio mensuales actuales?

## Conjunto de datos

El archivo `data/raw/guatemala_temperatura.csv` contiene **918 observaciones mensuales** desde enero de 1950 hasta junio de 2026.

Las variables incluyen:

- Temperatura del aire a 2 metros.
- Punto de rocío a 2 metros.
- Temperatura de la superficie.
- Temperaturas de cuatro capas del suelo.

La descripción completa de las variables se encuentra en [`codebook.md`](codebook.md).

## Metodología

El análisis incluye:

- Revisión de valores faltantes y duplicados.
- Resumen de extremos, promedios y rangos.
- Separación cronológica de los últimos 36 meses como prueba.
- Media móvil y descomposición aditiva.
- Tendencia lineal en grados Celsius por década.
- Pruebas ADF y KPSS para estacionariedad en media.
- Prueba de Fligner para estabilidad de varianza.
- Diferenciación estacional de 12 meses.
- Análisis de ACF y PACF.
- Entrenamiento y comparación de modelos SARIMA.
- Diagnóstico de residuos con Ljung-Box.
- Evaluación con MAE, RMSE y MAPE.
- Comparación con Holt-Winters, suavizamiento exponencial simple y naive estacional.

## Resultado principal

El análisis encontró una tendencia creciente en la temperatura promedio. Para la predicción fuera de muestra, el modelo **SARIMA(1,0,2)(1,1,0,12)** obtuvo el menor error entre los modelos SARIMA evaluados, con resultados aproximados de:

- **MAE:** 0.60 °C
- **RMSE:** 0.81 °C
- **MAPE:** 2.49 %

El modelo fue útil para estimar temperaturas promedio mensuales, aunque no sustituye un pronóstico meteorológico diario ni está diseñado para predecir eventos extremos.

## Archivos principales

```text
01_series_tiempo/
├── data/raw/guatemala_temperatura.csv
├── notebooks/series-tiempo.ipynb
├── codebook.md
├── README.md
└── requirements.txt
```

## Ejecutar el proyecto

Desde la raíz del repositorio:

```bash
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

Instalar dependencias:

```bash
pip install -r 01_series_tiempo/requirements.txt
```

Abrir el cuaderno:

```bash
jupyter notebook 01_series_tiempo/notebooks/series-tiempo.ipynb
```

## Versión publicada

El cuaderno se encuentra disponible como página web dentro del sitio del repositorio:

**https://vann06.github.io/Data-Science/01_series_tiempo/notebooks/series-tiempo.html**
