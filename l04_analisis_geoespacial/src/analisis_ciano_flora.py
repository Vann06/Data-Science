"""Galería de imágenes de cianobacteria por lago, agrupadas por año.

Arma un mosaico con todas las fechas oficiales de cada lago, organizadas por
fila de año, para ilustrar visualmente cómo evoluciona la floración a lo
largo del período estudiado (complementa el gráfico de línea de la sección 4
y los mapas puntuales de la sección 5).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from analisis_espacial import PROJECT_DIR, TEMPORAL_CSV, read_raster

OUTPUT_DIR = PROJECT_DIR / "outputs" / "galeria"
NOMBRES = {"atitlan": "Atitlán", "amatitlan": "Amatitlán"}


def build_gallery(lake: str, temporal: pd.DataFrame) -> Path:
    """Arma y guarda la galería de un lago: todas las fechas, agrupadas por año."""
    series = temporal.loc[temporal["lago"] == lake].copy().sort_values("fecha")
    series["anio"] = series["fecha"].dt.year

    imagenes = {}
    vmax_global = 0.0
    for row in series.itertuples():
        fecha_str = row.fecha.strftime("%Y-%m-%d")
        data, _ = read_raster(lake, fecha_str)
        imagenes[fecha_str] = data
        vmax_global = max(vmax_global, np.nanpercentile(data, 99))

    anios = sorted(series["anio"].unique())
    max_columnas = int(series.groupby("anio").size().max())

    figure, axes = plt.subplots(
        len(anios), max_columnas,
        figsize=(3.2 * max_columnas, 3.4 * len(anios)),
        squeeze=False,
    )

    for fila, anio in enumerate(anios):
        fechas_anio = series.loc[series["anio"] == anio, "fecha"].dt.strftime("%Y-%m-%d").tolist()
        for columna in range(max_columnas):
            axis = axes[fila][columna]
            axis.set_axis_off()
            if columna < len(fechas_anio):
                fecha_str = fechas_anio[columna]
                axis.imshow(imagenes[fecha_str], cmap="viridis", vmin=0, vmax=vmax_global)
                titulo = f"{anio} · {fecha_str}" if columna == 0 else fecha_str
                axis.set_title(titulo, fontsize=9)

    norm = Normalize(vmin=0, vmax=vmax_global)
    mappable = ScalarMappable(norm=norm, cmap="viridis")
    figure.colorbar(mappable, ax=axes, fraction=0.02, pad=0.02, label="Clorofila-a estimada")

    figure.suptitle(f"Galería de cianobacteria — {NOMBRES[lake]}", fontsize=14, fontweight="bold")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / f"{lake}_galeria_cianobacteria.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def pares_cronologicos(temporal: pd.DataFrame) -> pd.DataFrame:
    """Empareja las 11 fechas de cada lago por orden cronológico (1ra con 1ra, etc.).

    Las fechas oficiales no coinciden entre lagos, así que el emparejamiento es por
    posición en el tiempo, no por fecha exacta; se reporta la diferencia en días para
    que quede explícito qué tan cercanos están los dos momentos comparados.
    """
    atitlan = temporal.loc[temporal["lago"] == "atitlan"].sort_values("fecha").reset_index(drop=True)
    amatitlan = temporal.loc[temporal["lago"] == "amatitlan"].sort_values("fecha").reset_index(drop=True)
    n_pares = min(len(atitlan), len(amatitlan))

    pares = pd.DataFrame({
        "fecha_atitlan": atitlan.loc[: n_pares - 1, "fecha"],
        "fecha_amatitlan": amatitlan.loc[: n_pares - 1, "fecha"],
    })
    pares["diferencia_dias"] = (pares["fecha_atitlan"] - pares["fecha_amatitlan"]).dt.days.abs()
    return pares


def build_comparison_gallery(temporal: pd.DataFrame) -> Path:
    """Compara Atitlán y Amatitlán lado a lado, fila por orden cronológico de fecha.

    Usa una única escala de color compartida entre ambos lagos (a diferencia de
    `build_gallery`, que escala cada lago por separado) para que la intensidad visual
    refleje la diferencia real de magnitud entre lagos, no solo el patrón espacial.
    """
    pares = pares_cronologicos(temporal)

    imagenes = {}
    vmax_global = 0.0
    for lake, columna_fecha in (("atitlan", "fecha_atitlan"), ("amatitlan", "fecha_amatitlan")):
        for fecha in pares[columna_fecha]:
            fecha_str = fecha.strftime("%Y-%m-%d")
            data, _ = read_raster(lake, fecha_str)
            imagenes[(lake, fecha_str)] = data
            vmax_global = max(vmax_global, np.nanpercentile(data, 99))

    n_filas = len(pares)
    figure, axes = plt.subplots(n_filas, 2, figsize=(7, 3.2 * n_filas), squeeze=False)

    for fila, registro in enumerate(pares.itertuples()):
        for columna, (lake, fecha) in enumerate((
            ("atitlan", registro.fecha_atitlan),
            ("amatitlan", registro.fecha_amatitlan),
        )):
            fecha_str = fecha.strftime("%Y-%m-%d")
            axis = axes[fila][columna]
            axis.set_axis_off()
            axis.imshow(imagenes[(lake, fecha_str)], cmap="viridis", vmin=0, vmax=vmax_global)
            axis.set_title(f"{NOMBRES[lake]} · {fecha_str}", fontsize=9)

    norm = Normalize(vmin=0, vmax=vmax_global)
    mappable = ScalarMappable(norm=norm, cmap="viridis")
    figure.colorbar(mappable, ax=axes, fraction=0.03, pad=0.03, label="Clorofila-a estimada (escala compartida)")

    figure.suptitle(
        "Comparación de floraciones: Atitlán vs. Amatitlán\n(filas emparejadas por orden cronológico, no por fecha exacta)",
        fontsize=13, fontweight="bold",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "comparacion_lagos_cianobacteria.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def main() -> None:
    temporal = pd.read_csv(TEMPORAL_CSV, parse_dates=["fecha"])
    for lake in ("atitlan", "amatitlan"):
        archivo = build_gallery(lake, temporal)
        print(f"Galería generada: {archivo}")
    archivo_comparacion = build_comparison_gallery(temporal)
    print(f"Galería comparativa generada: {archivo_comparacion}")


if __name__ == "__main__":
    main()
