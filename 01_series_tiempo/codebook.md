# Codebook: temperatura promedio mensual — región de Guatemala

Conjunto de datos usado en `notebooks/series-de-tiempo-guatemala.ipynb`.
Archivo: `data/raw/guatemala_temperatura.csv` (918 observaciones mensuales,
enero 1950 a junio 2026, sin valores faltantes).

## Descripción

Temperatura promedio mensual (°C) de varias capas de la tierra en la región de
Guatemala, derivada de datos de reanálisis climático.

| Variable                     | Tipo (pandas)       | Descripción                                        |
|------------------------------|---------------------|----------------------------------------------------|
| month                        | datetime64 (índice) | Mes de la observación, frecuencia mensual `MS`     |
| year                         | int                 | Año de la observación                              |
| month_num                    | int                 | Número de mes (1–12)                               |
| dewpoint_2m_c                | float               | Punto de rocío a 2 m (°C)                          |
| temperature_2m_c             | float               | Temperatura del aire a 2 m (°C) — **serie modelada** |
| skin_temperature_c           | float               | Temperatura de la superficie (°C)                  |
| soil_temperature_layer_1_c   | float               | Temperatura del suelo, capa 1 (más superficial)    |
| soil_temperature_layer_2_c   | float               | Temperatura del suelo, capa 2                      |
| soil_temperature_layer_3_c   | float               | Temperatura del suelo, capa 3                      |
| soil_temperature_layer_4_c   | float               | Temperatura del suelo, capa 4 (más profunda)       |

## Características relevantes para el modelado

- **Estacionalidad anual** dominante (periodo = 12), amplitud estable de ~4–5 °C
  con máximo en abril–mayo: estacionalidad *aditiva*.
- **Tendencia** creciente suave (~+0.17 °C por década), acelerada desde ~1980.
- Varianza estable en el tiempo: no requiere transformación logarítmica; una
  **diferenciación estacional** (D=1, s=12) basta para lograr estacionariedad
  (confirmada con ADF y KPSS).
- A mayor profundidad de capa, menor amplitud del ciclo (el suelo profundo
  amortigua la estacionalidad).

## Partición

Se reservan los **últimos 36 meses** (julio 2023 a junio 2026) como conjunto de
prueba. La prueba es siempre posterior en el tiempo: los datos nunca se barajan.

