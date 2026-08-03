from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import unicodedata
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
RUTA_DATOS = ROOT / "data" / "raw" / "Base_Migracion_2009-2026jun.xlsx"
RUTA_SALIDA = ROOT / "L02_DL_series" / "data"

NOMBRES_SERIES = [
    "total_internacional",
    "aerea",
    "terrestre",
    "maritima",
    "america_centro",
    "america_norte",
    "europa",
]

TIPOS_COMPARABLES = {"turista", "excursionista"}

COLUMNAS_REQUERIDAS = {
    "Año",
    "Mes cod",
    "Vía",
    "País",
    "Región dos",
    "Tipo de Viajero",
    "Viajero",
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Normaliza texto a minúsculas, sin tildes y sin espacios laterales."""

    def limpiar(valor: object) -> str:
        texto = str(valor).strip().casefold()
        return "".join(
            caracter
            for caracter in unicodedata.normalize("NFKD", texto)
            if not unicodedata.combining(caracter)
        )

    return serie.fillna("").map(limpiar)


def cargar_datos(ruta: Path | str = RUTA_DATOS) -> pd.DataFrame:
    """Carga el Excel original, valida columnas y crea la columna mensual Fecha."""
    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            "No se encontró el archivo original de datos:\n"
            f"{ruta.resolve()}"
        )

    datos = pd.read_excel(
        ruta,
        sheet_name="Datos",
        engine="openpyxl",
    )

    faltantes = COLUMNAS_REQUERIDAS.difference(datos.columns)
    if faltantes:
        raise ValueError(
            "El Excel no contiene todas las columnas requeridas: "
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
        raise ValueError(f"Se encontraron {cantidad} fechas inválidas.")

    if datos["Viajero"].isna().any():
        cantidad = int(datos["Viajero"].isna().sum())
        raise ValueError(
            f"Se encontraron {cantidad} valores no numéricos en 'Viajero'."
        )

    if (datos["Viajero"] < 0).any():
        cantidad = int((datos["Viajero"] < 0).sum())
        raise ValueError(
            f"Se encontraron {cantidad} valores negativos en 'Viajero'."
        )

    return datos.sort_values("Fecha").reset_index(drop=True)


def _crear_serie_mensual(
    datos: pd.DataFrame,
    filtro: pd.Series,
    calendario: pd.DatetimeIndex,
) -> pd.Series:
    """Agrupa el total de viajeros por mes y completa el calendario mensual."""
    serie = (
        datos.loc[filtro]
        .groupby("Fecha")["Viajero"]
        .sum()
        .reindex(calendario, fill_value=0.0)
        .astype(float)
    )

    serie.index.name = "Fecha"
    return serie


def construir_series(datos: pd.DataFrame) -> pd.DataFrame:
    """
    Construye las siete series mensuales usadas en el Laboratorio 1.

    Definiciones:
    - total_internacional: Turista/Excursionista, excluyendo País=Guatemala.
    - aerea y terrestre: Turista/Excursionista.
    - maritima: todos los tipos de viajero, según la decisión metodológica de L1.
    - regiones: Turista/Excursionista y la columna 'Región dos'.
    """
    calendario = pd.date_range(
        start=datos["Fecha"].min(),
        end=datos["Fecha"].max(),
        freq="MS",
    )

    tipo = normalizar_texto(datos["Tipo de Viajero"])
    via = normalizar_texto(datos["Vía"])
    pais = normalizar_texto(datos["País"])
    region = normalizar_texto(datos["Región dos"])

    comparable = tipo.isin(TIPOS_COMPARABLES)

    filtros = {
        "total_internacional": comparable & pais.ne("guatemala"),
        "aerea": comparable & via.eq("aerea"),
        "terrestre": comparable & via.eq("terrestre"),
        "maritima": via.eq("maritima"),
        "america_centro": comparable
        & region.isin({"america del centro", "america central"}),
        "america_norte": comparable
        & region.isin({"america del norte", "norteamerica", "norte america"}),
        "europa": comparable & region.eq("europa"),
    }

    series = pd.DataFrame(
        {
            nombre: _crear_serie_mensual(datos, filtro, calendario)
            for nombre, filtro in filtros.items()
        },
        index=calendario,
    )

    series.index.name = "Fecha"

    # Validaciones estructurales.
    if list(series.columns) != NOMBRES_SERIES:
        raise AssertionError("El orden o nombre de las siete series cambió.")

    if series.index.has_duplicates:
        raise ValueError("El índice mensual contiene fechas duplicadas.")

    if not series.index.is_monotonic_increasing:
        raise ValueError("Las fechas no están ordenadas cronológicamente.")

    if series.isna().any().any():
        raise ValueError("Las series construidas contienen valores faltantes.")

    if not np.isfinite(series.to_numpy(dtype=float)).all():
        raise ValueError("Las series contienen valores infinitos.")

    if (series < 0).any().any():
        raise ValueError("Las series contienen valores negativos.")

    constantes = [
        nombre
        for nombre in series.columns
        if series[nombre].nunique(dropna=True) <= 1
    ]

    if constantes:
        categorias_region = sorted(region[region.ne("")].unique().tolist())
        raise ValueError(
            "Se construyeron series constantes, lo cual normalmente indica "
            f"un filtro incorrecto. Series: {constantes}. "
            "Valores encontrados en 'Región dos': "
            f"{categorias_region}"
        )

    return series


def resumir_series(series: pd.DataFrame) -> pd.DataFrame:
    """Genera una tabla de control para documentar las siete series."""
    return pd.DataFrame(
        {
            "observaciones": series.count(),
            "valores_faltantes": series.isna().sum(),
            "valores_unicos": series.nunique(),
            "ceros": (series == 0).sum(),
            "minimo": series.min(),
            "maximo": series.max(),
            "media": series.mean(),
            "desviacion": series.std(ddof=1),
        }
    )


def extraer_catch22(series: pd.DataFrame) -> pd.DataFrame:
    """
    Extrae exactamente las 22 características catch22 para cada serie.

    El argumento catch24=False se deja explícito para no agregar media
    ni desviación estándar y cumplir exactamente con el inciso 2.2.
    """
    try:
        from pycatch22 import catch22_all
    except ImportError as exc:
        raise ImportError(
            "No está instalado pycatch22 en el entorno activo. "
            "Ejecuta: python -m pip install pycatch22"
        ) from exc

    resultados: list[dict[str, float | str]] = []

    for nombre in series.columns:
        valores = series[nombre].to_numpy(dtype=float)

        if not np.isfinite(valores).all():
            raise ValueError(f"La serie '{nombre}' contiene NaN o infinitos.")

        if np.unique(valores).size <= 1:
            raise ValueError(f"La serie '{nombre}' es constante.")

        resultado = catch22_all(
            valores.tolist(),
            catch24=False,
        )

        nombres = resultado["names"]
        valores_features = resultado["values"]

        if len(nombres) != 22 or len(valores_features) != 22:
            raise AssertionError(
                f"Se esperaban 22 características para '{nombre}', "
                f"pero se obtuvieron {len(valores_features)}."
            )

        fila: dict[str, float | str] = {"serie": nombre}
        fila.update(dict(zip(nombres, valores_features)))
        resultados.append(fila)

    matriz = pd.DataFrame(resultados).set_index("serie")
    matriz.index.name = "serie"

    if matriz.shape != (7, 22):
        raise AssertionError(
            f"La matriz catch22 debe ser (7, 22), no {matriz.shape}."
        )

    if matriz.columns.duplicated().any():
        raise ValueError("La matriz catch22 contiene columnas duplicadas.")

    valores = matriz.to_numpy(dtype=float)
    if not np.isfinite(valores).all():
        ubicaciones = np.argwhere(~np.isfinite(valores))
        detalle = [
            {
                "serie": matriz.index[fila],
                "caracteristica": matriz.columns[columna],
                "valor": valores[fila, columna],
            }
            for fila, columna in ubicaciones
        ]
        raise ValueError(
            "Catch22 produjo valores no finitos. "
            f"Detalle: {detalle}"
        )

    return matriz


def estandarizar_catch22(
    matriz: pd.DataFrame,
) -> tuple[pd.DataFrame, StandardScaler]:
    """
    Estandariza cada característica entre las siete series.

    StandardScaler calcula:
        z = (x - media_de_la_caracteristica) / desviacion_de_la_caracteristica

    El ajuste se realiza una sola vez usando la matriz completa.
    """
    if matriz.shape != (7, 22):
        raise ValueError(
            f"Se esperaba una matriz (7, 22), no {matriz.shape}."
        )

    columnas_constantes = matriz.columns[
        matriz.nunique(dropna=False) <= 1
    ].tolist()

    if columnas_constantes:
        warnings.warn(
            "Las siguientes características son constantes entre las siete "
            "series y no aportan separación comparativa: "
            f"{columnas_constantes}",
            RuntimeWarning,
        )

    escalador = StandardScaler()
    valores_escalados = escalador.fit_transform(matriz)

    matriz_escalada = pd.DataFrame(
        valores_escalados,
        index=matriz.index.copy(),
        columns=matriz.columns.copy(),
    )
    matriz_escalada.index.name = "serie"

    if not np.isfinite(matriz_escalada.to_numpy()).all():
        raise ValueError("La matriz estandarizada contiene NaN o infinitos.")

    return matriz_escalada, escalador


def guardar_resultados(
    series: pd.DataFrame,
    matriz_catch22: pd.DataFrame,
    matriz_catch22_scaled: pd.DataFrame,
    ruta_salida: Path | str = RUTA_SALIDA,
) -> dict[str, Path]:
    """Guarda los tres CSV principales con precisión numérica reproducible."""
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(parents=True, exist_ok=True)

    rutas = {
        "series": ruta_salida / "series_mensuales.csv",
        "catch22": ruta_salida / "catch22_features.csv",
        "catch22_scaled": ruta_salida / "catch22_features_scaled.csv",
    }

    series.to_csv(
        rutas["series"],
        index=True,
        encoding="utf-8-sig",
        float_format="%.17g",
    )

    matriz_catch22.to_csv(
        rutas["catch22"],
        index=True,
        encoding="utf-8-sig",
        float_format="%.17g",
    )

    matriz_catch22_scaled.to_csv(
        rutas["catch22_scaled"],
        index=True,
        encoding="utf-8-sig",
        float_format="%.17g",
    )

    return rutas


def obtener_version_pycatch22() -> str:
    """Retorna la versión instalada para documentar reproducibilidad."""
    try:
        return version("pycatch22")
    except PackageNotFoundError:
        return "no instalado"


def main() -> None:
    """Ejecuta el pipeline completo y guarda los tres CSV principales."""
    print("1. Cargando datos...")
    datos = cargar_datos()

    print("2. Construyendo las siete series...")
    series = construir_series(datos)
    print(resumir_series(series).round(2).to_string())

    print("\n3. Extrayendo exactamente 22 características por serie...")
    matriz = extraer_catch22(series)

    print("4. Estandarizando la matriz completa...")
    matriz_escalada, _ = estandarizar_catch22(matriz)

    rutas = guardar_resultados(
        series,
        matriz,
        matriz_escalada,
    )

    print("\nProceso completado correctamente.")
    print(f"Versión pycatch22: {obtener_version_pycatch22()}")
    print(f"Series: {series.shape}")
    print(f"Catch22 sin escalar: {matriz.shape}")
    print(f"Catch22 estandarizado: {matriz_escalada.shape}")

    for nombre, ruta in rutas.items():
        print(f"{nombre}: {ruta.resolve()}")


if __name__ == "__main__":
    main()