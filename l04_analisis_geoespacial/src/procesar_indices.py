"""Genera NDVI y NDWI para las escenas raster descargadas de Sentinel-2.

Entradas:
    data/<lago>/<fecha>_bandas.tif

Salidas:
    data/indices/<lago>_<fecha>_ndvi.tif
    data/indices/<lago>_<fecha>_ndwi.tif
"""

from pathlib import Path

import numpy as np
import rasterio


SOURCE_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = SOURCE_DIR / "indices"
EXPECTED_BANDS = ("B02", "B03", "B04", "B05", "B07", "B8A", "B08", "B11", "B12")


def write_index(path: Path, profile: dict, name: str, data: np.ndarray) -> None:
    """Escribe un índice como GeoTIFF de una banda, con NoData igual a NaN."""
    with rasterio.open(path, "w", **profile) as destination:
        destination.write(data, 1)
        destination.set_band_description(1, name.upper())


def process_scene(path: Path) -> None:
    """Calcula NDVI y NDWI para una escena Sentinel-2 de nueve bandas."""
    lake = path.parent.name
    scene_date = path.stem.removesuffix("_bandas")

    with rasterio.open(path) as source:
        if source.descriptions != EXPECTED_BANDS:
            raise ValueError(f"Orden de bandas inesperado en {path}: {source.descriptions}")
        profile = source.profile.copy()
        nodata = source.nodata
        green = source.read(2).astype("float32")  # B03
        red = source.read(3).astype("float32")  # B04
        nir = source.read(7).astype("float32")  # B08

    # Valores negativos o NoData no representan reflectancia útil para índices normalizados.
    invalid = (green == nodata) | (red == nodata) | (nir == nodata)
    invalid |= (green < 0) | (red < 0) | (nir < 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)
        ndwi = (green - nir) / (green + nir)

    profile.update(count=1, dtype="float32", nodata=np.nan, compress="deflate")
    for name, index in (("ndvi", ndvi), ("ndwi", ndwi)):
        # Con reflectancias no negativas, ambos índices normalizados deben quedar en [-1, 1].
        index[invalid | ~np.isfinite(index) | (index < -1) | (index > 1)] = np.nan
        write_index(OUTPUT_DIR / f"{lake}_{scene_date}_{name}.tif", profile, name, index)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    scenes = sorted(SOURCE_DIR.glob("*/*_bandas.tif"))
    if len(scenes) != 22:
        raise ValueError(f"Se esperaban 22 escenas oficiales; se encontraron {len(scenes)}.")
    for scene in scenes:
        process_scene(scene)
    print(f"Proceso completado: {len(scenes) * 2} GeoTIFF de NDVI/NDWI en {OUTPUT_DIR}.")


if __name__ == "__main__":
    main()
