# Codebook - Temperatura mensual de Guatemala

El archivo `data/raw/guatemala_temperatura.csv` contiene 918 observaciones mensuales desde enero de 1950 hasta junio de 2026. No tiene fechas duplicadas ni valores faltantes.

| Variable | Tipo | Descripción |
|---|---|---|
| `month` | fecha | Primer día de cada mes; índice temporal principal. |
| `year` | entero | Año calendario. |
| `month_num` | entero | Número de mes, de 1 a 12. |
| `dewpoint_2m_c` | decimal | Temperatura de punto de rocío a 2 metros, en °C. |
| `temperature_2m_c` | decimal | Temperatura promedio del aire a 2 metros, en °C. Es la serie principal del modelado. |
| `skin_temperature_c` | decimal | Temperatura promedio de la superficie, en °C. |
| `soil_temperature_layer_1_c` | decimal | Temperatura de la primera capa del suelo, en °C. |
| `soil_temperature_layer_2_c` | decimal | Temperatura de la segunda capa del suelo, en °C. |
| `soil_temperature_layer_3_c` | decimal | Temperatura de la tercera capa del suelo, en °C. |
| `soil_temperature_layer_4_c` | decimal | Temperatura de la cuarta capa del suelo, en °C. |

## Convenciones

- Frecuencia: mensual, inicio de mes (`MS`).
- Unidad de las variables meteorológicas: grados Celsius.
- Datos crudos: no deben modificarse directamente.
- Conjunto de prueba: últimos 36 meses, julio de 2023 a junio de 2026.
