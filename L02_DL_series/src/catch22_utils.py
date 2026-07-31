import numpy as np
import pandas as pd

from pycatch22 import catch22_all
from sklearn.preprocessing import StandardScaler


def extraer_catch22(
    series: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extrae las 22 características catch22 para cada serie.

    Cada fila representa una serie.
    Cada columna representa una característica.
    """
    resultados = []

    for nombre_serie in series.columns:
        valores = (
            pd.to_numeric(
                series[nombre_serie],
                errors="coerce",
            )
            .dropna()
            .to_numpy(dtype=float)
        )

        if len(valores) == 0:
            raise ValueError(
                f"La serie {nombre_serie} no contiene datos válidos."
            )

        resultado = catch22_all(valores)

        fila = dict(
            zip(
                resultado["names"],
                resultado["values"],
            )
        )

        fila["serie"] = nombre_serie
        resultados.append(fila)

    matriz = (
        pd.DataFrame(resultados)
        .set_index("serie")
    )

    valores_matriz = matriz.to_numpy(dtype=float)

    if not np.isfinite(valores_matriz).all():
        columnas_problematicas = matriz.columns[
            ~np.isfinite(valores_matriz).all(axis=0)
        ].tolist()

        raise ValueError(
            "Catch22 produjo valores no finitos en: "
            f"{columnas_problematicas}"
        )

    return matriz


def estandarizar_catch22(
    matriz: pd.DataFrame,
) -> pd.DataFrame:
    """
    Estandariza las características usando media 0 y desviación 1.
    """
    escalador = StandardScaler()

    valores_escalados = escalador.fit_transform(matriz)

    matriz_escalada = pd.DataFrame(
        valores_escalados,
        index=matriz.index,
        columns=matriz.columns,
    )

    matriz_escalada.index.name = "serie"

    return matriz_escalada