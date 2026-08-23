"""Descarga las 9 bandas espectrales que necesita `parte_2/src/preparar_ml.py`
para las 22 escenas oficiales de Atitlán y Amatitlán.

Usa openEO (Copernicus Data Space) para cargar B02, B03, B04, B05, B07, B8A,
B08, B11 y B12 de Sentinel-2 L2A y descarga un único GeoTIFF multibanda por
lago y fecha en `data/<lago>/<fecha>_bandas.tif`, que es lo que espera
`parte_2/src/preparar_ml.py` (constante `BANDAS`). Si un archivo ya existe, se
omite su descarga.

Las coordenadas de los lagos y las 22 fechas oficiales son las mismas que usa
`descargar_indices.py` (Parte I) para NDVI/NDWI.

Uso:
    python src/descargar_bandas.py
"""

from datetime import datetime, timedelta
from pathlib import Path

import openeo
import rasterio

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "data"

# Mismo orden que `BANDAS` en parte_2/src/preparar_ml.py — preparar_ml.py
# valida `source.descriptions == BANDAS` y falla si el orden no coincide.
BANDAS = ("B02", "B03", "B04", "B05", "B07", "B8A", "B08", "B11", "B12")

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
    """Carga las 9 bandas de Sentinel-2 L2A para una fecha y un lago."""
    inicio = datetime.strptime(fecha, "%Y-%m-%d")
    fin = inicio + timedelta(days=1)
    return connection.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=lago,
        temporal_extent=[inicio.strftime("%Y-%m-%d"), fin.strftime("%Y-%m-%d")],
        bands=list(BANDAS),
    )


def estampar_descripciones(archivo: Path) -> None:
    """Fuerza los nombres de banda en el GeoTIFF descargado.

    openEO no siempre conserva las etiquetas de banda al exportar a GTiff, y
    preparar_ml.py exige que `source.descriptions == BANDAS` exactamente.
    """
    with rasterio.open(archivo, "r+") as destino:
        for indice, nombre in enumerate(BANDAS, start=1):
            destino.set_band_description(indice, nombre)


def descargar_fecha(connection, lago, nombre_lago, fecha, sobrescribir=False):
    """Descarga el GeoTIFF de 9 bandas de una fecha si aún no está en disco."""
    carpeta = OUTPUT_DIR / nombre_lago
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo_bandas = carpeta / f"{fecha}_bandas.tif"

    if archivo_bandas.exists() and not sobrescribir:
        print(f"  Reutilizando {nombre_lago} — {fecha}")
        return

    cube = cargar_fecha(connection, lago, fecha)
    cube.save_result(format="GTiff").download(str(archivo_bandas))
    estampar_descripciones(archivo_bandas)
    print(f"  Descargado {archivo_bandas.relative_to(PROJECT_DIR)}")


def main():
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

    print(f"Listo: GeoTIFF de 9 bandas de las 22 escenas en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
