"""Correlación espacial entre cianobacteria, NDVI y NDWI por lago y fecha."""

from pathlib import Path
from typing import Literal, TypeAlias

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio

from analisis_espacial import PROJECT_DIR, TEMPORAL_CSV, read_raster


INDEX_DIR = PROJECT_DIR / "data" / "indices"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "correlacion"
MAX_SAMPLES_PER_DATE = 50_000
RNG = np.random.default_rng(3084)
IndexName: TypeAlias = Literal["ndvi", "ndwi"]
ScatterKey: TypeAlias = tuple[str, IndexName]


def read_index(lake: str, date: str, index: str) -> np.ndarray:
    """Lee un índice derivado, descarta NoData y valores fuera de [-1, 1]."""
    path = INDEX_DIR / f"{lake}_{date}_{index}.tif"
    with rasterio.open(path) as source:
        data = source.read(1).astype("float32")
        nodata = source.nodata
    if nodata is not None:
        data[data == nodata] = np.nan
    data[~np.isfinite(data) | (data < -1) | (data > 1)] = np.nan
    return data


def sample_pairs(cyano: np.ndarray, index: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve pares válidos y una muestra reproducible si hay demasiados píxeles."""
    valid = np.isfinite(cyano) & np.isfinite(index)
    x, y = index[valid], cyano[valid]
    if len(x) > MAX_SAMPLES_PER_DATE:
        selected = RNG.choice(len(x), MAX_SAMPLES_PER_DATE, replace=False)
        x, y = x[selected], y[selected]
    return x, y


def strength(r: float) -> str:
    magnitude = abs(r)
    if magnitude < 0.2:
        return "débil"
    if magnitude < 0.5:
        return "moderada"
    return "fuerte"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temporal = pd.read_csv(TEMPORAL_CSV, parse_dates=["fecha"])
    rows = []
    scatter: dict[ScatterKey, list[tuple[np.ndarray, np.ndarray]]] = {
        ("atitlan", "ndvi"): [],
        ("atitlan", "ndwi"): [],
        ("amatitlan", "ndvi"): [],
        ("amatitlan", "ndwi"): [],
    }

    for record in temporal.itertuples():
        lake = str(record.lago)
        # Se usa texto ISO porque `itertuples()` se tipa como Scalar en Pylance.
        date = str(record.fecha)[:10]
        cyano, _ = read_raster(lake, date)
        for index_name in ("ndvi", "ndwi"):
            index = read_index(lake, date, index_name)
            if cyano.shape != index.shape:
                raise ValueError(f"Mallas distintas en {lake} {date}: {cyano.shape} vs {index.shape}")
            x, y = sample_pairs(cyano, index)
            r = float(np.corrcoef(x, y)[0, 1])
            rows.append({"lago": lake, "fecha": date, "indice": index_name.upper(), "pearson_r": r, "pixeles_usados": len(x)})
            scatter[(lake, index_name)].append((x, y))

    correlations = pd.DataFrame(rows)
    correlations.to_csv(OUTPUT_DIR / "correlacion_por_fecha.csv", index=False)
    summary = correlations.groupby(["lago", "indice"], as_index=False).agg(
        pearson_mediano=("pearson_r", "median"),
        pearson_promedio=("pearson_r", "mean"),
        minimo=("pearson_r", "min"),
        maximo=("pearson_r", "max"),
    )
    summary["interpretacion"] = summary["pearson_mediano"].apply(
        lambda r: f"{'positiva' if r >= 0 else 'negativa'} {strength(r)}"
    )
    summary.to_csv(OUTPUT_DIR / "resumen_correlacion.csv", index=False)

    figure, axes = plt.subplots(2, 2, figsize=(12, 10))
    for axis, (lake, index_name) in zip(axes.ravel(), scatter):
        x = np.concatenate([pair[0] for pair in scatter[(lake, index_name)]])
        y = np.concatenate([pair[1] for pair in scatter[(lake, index_name)]])
        axis.hexbin(x, y, gridsize=55, mincnt=1, cmap="viridis")
        median_r = summary.loc[(summary.lago == lake) & (summary.indice == index_name.upper()), "pearson_mediano"].iloc[0]
        axis.set(title=f"{lake.title()}: cianobacteria vs {index_name.upper()}\nr mediano = {median_r:.3f}", xlabel=index_name.upper(), ylabel="Clorofila-a estimada")
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "dispersion_cianobacteria_indices.png", dpi=250, bbox_inches="tight")
    plt.close(figure)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
