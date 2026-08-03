import pandas as pd


TIPOS_COMPARABLES = [
    "Turista",
    "Excursionista",
]


def _crear_serie_mensual(
    datos: pd.DataFrame,
    filtro: pd.Series,
    calendario: pd.DatetimeIndex,
) -> pd.Series:
    """
    Suma los viajeros por mes y completa el calendario mensual.
    """
    serie = (
        datos.loc[filtro]
        .groupby("Fecha")["Viajero"]
        .sum()
        .reindex(calendario, fill_value=0)
        .astype(float)
    )

    serie.index.name = "Fecha"

    return serie


def _obtener_columna_region(datos: pd.DataFrame) -> str:
    """
    Identifica la columna que contiene las regiones geográficas.
    """
    opciones = [
        "Región dos",
        "Agrupación Residencia",
    ]

    for columna in opciones:
        if columna in datos.columns:
            return columna

    raise KeyError(
        "No se encontró una columna de región. "
        f"Se esperaba una de estas: {opciones}"
    )


def construir_series(datos: pd.DataFrame) -> pd.DataFrame:
    """
    Construye las siete series mensuales utilizadas en los laboratorios.

    Retorna
    -------
    pd.DataFrame
        Una columna por serie y una fila por mes.
    """
    calendario = pd.date_range(
        start=datos["Fecha"].min(),
        end=datos["Fecha"].max(),
        freq="MS",
    )

    tipos_comparables = datos["Tipo de Viajero"].isin(
        TIPOS_COMPARABLES
    )

    via = datos["Vía"].astype(str).str.strip()
    pais = datos["País"].astype(str).str.strip()

    columna_region = _obtener_columna_region(datos)

    region = (
        datos[columna_region]
        .astype(str)
        .str.strip()
    )

    # Serie total internacional:
    # Turista y Excursionista, excluyendo Guatemala.
    total = _crear_serie_mensual(
        datos,
        tipos_comparables & pais.ne("Guatemala"),
        calendario,
    )

    # Vías aérea y terrestre:
    # Turista y Excursionista.
    aerea = _crear_serie_mensual(
        datos,
        tipos_comparables & via.eq("Aérea"),
        calendario,
    )

    terrestre = _crear_serie_mensual(
        datos,
        tipos_comparables & via.eq("Terrestre"),
        calendario,
    )

    # Marítima:
    # Se conservan todos los tipos de viajero según la decisión de L1.
    maritima = _crear_serie_mensual(
        datos,
        via.eq("Marítima"),
        calendario,
    )

    america_centro = _crear_serie_mensual(
        datos,
        tipos_comparables
        & region.eq("América del Centro"),
        calendario,
    )

    america_norte = _crear_serie_mensual(
        datos,
        tipos_comparables
        & region.eq("América del Norte"),
        calendario,
    )

    europa = _crear_serie_mensual(
        datos,
        tipos_comparables
        & region.eq("Europa"),
        calendario,
    )

    series = pd.DataFrame(
        {
            "total_internacional": total,
            "aerea": aerea,
            "terrestre": terrestre,
            "maritima": maritima,
            "america_centro": america_centro,
            "america_norte": america_norte,
            "europa": europa,
        }
    )

    if series.isna().any().any():
        raise ValueError(
            "Las series construidas contienen valores faltantes."
        )

    if not series.index.is_monotonic_increasing:
        raise ValueError(
            "Las fechas no están ordenadas cronológicamente."
        )

    if len(series) != 210:
        print(
            "Advertencia: se esperaban 210 meses, "
            f"pero se construyeron {len(series)}."
        )

    return series