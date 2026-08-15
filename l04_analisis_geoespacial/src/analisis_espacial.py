"""Análisis espacial de los GeoTIFF de cianobacteria de Atitlán y Amatitlán.

Genera mapas de distribución para las fechas pico, comparaciones entre la fecha
más baja y la fecha pico, y mapas de persistencia de valores relativamente altos.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import label
from rasterio.plot import plotting_extent


PROJECT_DIR = Path(__file__).resolve().parents[1]
CYANO_DIR = PROJECT_DIR / "notebooks" / "resultados_cyano"
TEMPORAL_CSV = PROJECT_DIR / "notebooks" / "resultados_temporales_cianobacteria.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "espacial"


def read_raster(lake: str, date: str) -> tuple[np.ndarray, dict]:
    """Lee una estimación de clorofila-a y convierte NoData/negativos a NaN."""
    path = CYANO_DIR / f"{lake}_{date}.tif"
    with rasterio.open(path) as source:
        data = source.read(1).astype("float32")
        profile = source.profile
        nodata = source.nodata
    if nodata is not None:
        data[data == nodata] = np.nan
    data[~np.isfinite(data) | (data < 0)] = np.nan
    # El script espectral puede clasificar píxeles aislados fuera del lago como agua.
    # Se conserva únicamente el componente espacial continuo más grande: el lago.
    components, count = label(np.isfinite(data))
    if count:
        sizes = np.bincount(components.ravel())
        sizes[0] = 0
        lake_component = sizes.argmax()
        data[components != lake_component] = np.nan
    return data, profile


def format_map(axis: plt.Axes, image, title: str, units: str) -> None:
    axis.set_title(title)
    axis.set_xlabel("Este UTM (m)")
    axis.set_ylabel("Norte UTM (m)")
    colorbar = plt.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    colorbar.set_label(units)


def persistence_and_centroid(stack: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """Calcula frecuencia espacial del 10% superior de cada fecha y su centro."""
    high_masks = []
    for image in stack:
        valid = image[np.isfinite(image)]
        threshold = np.nanpercentile(valid, 90)
        high_masks.append((image >= threshold) & np.isfinite(image))
    high_masks = np.stack(high_masks)
    observed = np.sum(np.isfinite(stack), axis=0)
    frequency = np.divide(
        np.sum(high_masks, axis=0) * 100,
        observed,
        out=np.full(observed.shape, np.nan, dtype="float32"),
        where=observed > 0,
    )
    persistent = frequency >= 50
    fraction_persistent = float(np.nanmean(persistent) * 100)
    rows, columns = np.where(persistent)
    if len(rows) == 0:
        return frequency, fraction_persistent, np.nan, np.nan
    return frequency, fraction_persistent, float(rows.mean()), float(columns.mean())


def describe_position(row: float, column: float, shape: tuple[int, int]) -> str:
    """Describe la ubicación relativa del centro de persistencia en el mapa."""
    if not np.isfinite(row):
        return "sin zona persistente con el criterio del 50% de fechas"
    vertical = "norte" if row < shape[0] / 3 else "sur" if row > shape[0] * 2 / 3 else "centro"
    horizontal = "oeste" if column < shape[1] / 3 else "este" if column > shape[1] * 2 / 3 else "centro"
    return f"sector {vertical}-{horizontal}"


def analyze_lake(lake: str, temporal: pd.DataFrame) -> dict:
    """Crea mapas y obtiene un resumen espacial para un lago."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    series = temporal.loc[temporal["lago"] == lake].copy().sort_values("fecha")
    low_date = series.loc[series["promedio_cyano"].idxmin(), "fecha"]
    peak_date = series.loc[series["promedio_cyano"].idxmax(), "fecha"]
    images, profiles = zip(*(read_raster(lake, row.fecha.strftime("%Y-%m-%d")) for row in series.itertuples()))
    stack = np.stack(images)
    extent = plotting_extent(stack[0], profiles[0]["transform"])
    vmax = float(np.nanpercentile(stack, 99))
    low, _ = read_raster(lake, low_date.strftime("%Y-%m-%d"))
    peak, _ = read_raster(lake, peak_date.strftime("%Y-%m-%d"))
    frequency, persistent_pct, row, column = persistence_and_centroid(stack)

    figure, axis = plt.subplots(figsize=(8, 6))
    image = axis.imshow(peak, cmap="viridis", vmin=0, vmax=vmax, extent=extent)
    format_map(axis, image, f"{lake.title()}: distribución en la fecha pico ({peak_date:%Y-%m-%d})", "Clorofila-a estimada")
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / f"{lake}_mapa_pico.png", dpi=250, bbox_inches="tight")
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(13, 6), sharex=True, sharey=True)
    for axis, data, selected_date, label in zip(axes, (low, peak), (low_date, peak_date), ("Fecha baja", "Fecha pico")):
        image = axis.imshow(data, cmap="viridis", vmin=0, vmax=vmax, extent=extent)
        format_map(axis, image, f"{lake.title()}: {label}\n{selected_date:%Y-%m-%d}", "Clorofila-a estimada")
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / f"{lake}_comparacion_bajo_vs_pico.png", dpi=250, bbox_inches="tight")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 6))
    image = axis.imshow(frequency, cmap="magma", vmin=0, vmax=100, extent=extent)
    format_map(axis, image, f"{lake.title()}: persistencia de valores altos", "% de fechas en el 10% superior")
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / f"{lake}_persistencia_alta.png", dpi=250, bbox_inches="tight")
    plt.close(figure)

    return {
        "lago": lake,
        "fecha_baja": low_date.strftime("%Y-%m-%d"),
        "fecha_pico": peak_date.strftime("%Y-%m-%d"),
        "vmax_visualizacion_p99": vmax,
        "porcentaje_area_persistente": persistent_pct,
        "ubicacion_persistencia": describe_position(row, column, stack.shape[1:]),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temporal = pd.read_csv(TEMPORAL_CSV, parse_dates=["fecha"])
    if temporal.groupby("lago").size().to_dict() != {"amatitlan": 11, "atitlan": 11}:
        raise ValueError("La tabla temporal debe contener las 11 fechas oficiales de cada lago.")
    summary = pd.DataFrame([analyze_lake(lake, temporal) for lake in ("atitlan", "amatitlan")])
    summary.to_csv(OUTPUT_DIR / "resumen_espacial.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
