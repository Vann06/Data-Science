"""Descarga NDVI y NDWI para las 22 escenas oficiales de Atitlán y Amatitlán.

Usa openEO (Copernicus Data Space) para cargar únicamente B03, B04 y B08 de
Sentinel-2 L2A, calcula los índices en la nube y descarga un GeoTIFF de una
banda por índice, lago y fecha en `data/indices/`, que es lo que espera
`analisis_correlacion.py`. Si un archivo ya existe, se omite su descarga.

Uso:
    python src/descargar_indices.py
"""

from datetime import datetime, timedelta
from pathlib import Path

import openeo

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "data" / "indices"

LAGO_ATITLAN = {
    "west": -91.326256, "east": -91.071510,
    "south": 14.594800, "north": 14.750979,
}
LAGO_AMATITLAN = {
    "west": -90.638065, "east": -90.512924,
    "south": 14.412347, "north": 14.493799,
}

FECHAS_ATITLAN = [
    "2025-01-18", "2025-04-13", "2025-05-13", "2025-07-17",
    "2025-11-21", "2025-12-29", "2026-02-12", "2026-03-24",
    "2026-04-13", "2026-04-28", "2026-07-22",
]
FECHAS_AMATITLAN = [
    "2025-01-28", "2025-04-15", "2025-04-28", "2025-11-24",
    "2026-01-08", "2026-02-02", "2026-02-07", "2026-03-29",
    "2026-04-13", "2026-04-28", "2026-06-19",
]


def cargar_fecha(connection, lago, fecha):
    """Carga B03, B04 y B08 de Sentinel-2 L2A para una fecha y un lago."""
    inicio = datetime.strptime(fecha, "%Y-%m-%d")
    fin = inicio + timedelta(days=1)
    return connection.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=lago,
        temporal_extent=[inicio.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d")],
        bands=["B03", "B04", "B08"],
    )


def descargar_fecha(connection, lago, nombre_lago, fecha, sobrescribir=False):
    """Descarga NDVI y NDWI de una fecha si aún no están en disco."""
    archivo_ndvi = OUTPUT_DIR / f"{nombre_lago}_{fecha}_ndvi.tif"
    archivo_ndwi = OUTPUT_DIR / f"{nombre_lago}_{fecha}_ndwi.tif"

    if archivo_ndvi.exists() and archivo_ndwi.exists() and not sobrescribir:
        print(f"  Reutilizando {nombre_lago} — {fecha}")
        return

    cube = cargar_fecha(connection, lago, fecha)
    b03, b04, b08 = cube.band("B03"), cube.band("B04"), cube.band("B08")

    if sobrescribir or not archivo_ndvi.exists():
        ndvi = (b08 - b04) / (b08 + b04)
        ndvi.save_result(format="GTiff").download(str(archivo_ndvi))
        print(f"  Descargado {archivo_ndvi.name}")

    if sobrescribir or not archivo_ndwi.exists():
        ndwi = (b03 - b08) / (b03 + b08)
        ndwi.save_result(format="GTiff").download(str(archivo_ndwi))
        print(f"  Descargado {archivo_ndwi.name}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = openeo.connect("openeo.dataspace.copernicus.eu")
    connection.authenticate_oidc()
    print("Conexión realizada correctamente")

    for lago, nombre_lago, fechas in (
        (LAGO_ATITLAN, "atitlan", FECHAS_ATITLAN),
        (LAGO_AMATITLAN, "amatitlan", FECHAS_AMATITLAN),
    ):
        for fecha in fechas:
            print(f"Procesando {nombre_lago.capitalize()} — {fecha}")
            descargar_fecha(connection, lago, nombre_lago, fecha)

    print(f"Listo: NDVI y NDWI de las 22 escenas en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
