from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

RUTA_DATOS = (
    ROOT
    / "data"
    / "raw"
    / "Base_Migracion_2009-2026jun.xlsx"
)

COLUMNAS_REQUERIDAS = {
    "Año",
    "Mes cod",
    "Vía",
    "País",
    "Tipo de Viajero",
    "Viajero",
}


def cargar_datos(ruta: Path | str = RUTA_DATOS) -> pd.DataFrame:
    """
    Carga la base original de migración y crea la columna Fecha.

    Retorna
    -------
    pd.DataFrame
        Base ordenada cronológicamente.
    """
    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de datos:\n{ruta.resolve()}"
        )

    datos = pd.read_excel(
        ruta,
        sheet_name="Datos",
        engine="openpyxl",
    )

    faltantes = COLUMNAS_REQUERIDAS.difference(datos.columns)

    if faltantes:
        raise ValueError(
            "La base no contiene las columnas requeridas: "
            f"{sorted(faltantes)}"
        )

    datos = datos.copy()

    datos["Viajero"] = pd.to_numeric(
        datos["Viajero"],
        errors="coerce",
    )

    datos["Fecha"] = pd.to_datetime(
        {
            "year": datos["Año"],
            "month": datos["Mes cod"],
            "day": 1,
        },
        errors="coerce",
    )

    if datos["Fecha"].isna().any():
        cantidad = int(datos["Fecha"].isna().sum())
        raise ValueError(
            f"Se encontraron {cantidad} fechas inválidas."
        )

    if datos["Viajero"].isna().any():
        cantidad = int(datos["Viajero"].isna().sum())
        raise ValueError(
            f"Se encontraron {cantidad} valores inválidos en Viajero."
        )

    datos = (
        datos
        .sort_values("Fecha")
        .reset_index(drop=True)
    )

    return datos