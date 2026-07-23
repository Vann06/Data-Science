# Codebook: Base Migración 2009 - 2026 

Conjunto de datos usado en `notebooks/series-de-tiempo.ipynb`.
Archivo: `data/raw/Base_Migracion_2009_2026.csv`

## Descripción

Base de datos de migración en Guatemala entre los años 2009 y 2026.

| Variable                     | Tipo (pandas)       | Descripción                                        |
|------------------------------|---------------------|----------------------------------------------------|
| month                        | datetime64 (índice) | Mes de la observación, frecuencia mensual `MS`     |
| year                         | int                 | Año de la observación                              |
| month_num                    | int                 | Número de mes (1–12)                               |
| dewpoint_2m_c                | float               | Punto de rocío a 2 m (°C)                          |

## Características relevantes para el modelado

- **Estacionalidad anual** dominante (periodo = 12), amplitud estable de ~4–5 °C
  con máximo en abril–mayo: estacionalidad *aditiva*.
- **Tendencia** creciente suave (~+0.17 °C por década), acelerada desde ~1980.
- Varianza estable en el tiempo: no requiere transformación logarítmica; una
  **diferenciación estacional** (D=1, s=12) basta para lograr estacionariedad
  (confirmada con ADF y KPSS).
- A mayor profundidad de capa, menor amplitud del ciclo (el suelo profundo
  amortigua la estacionalidad).
