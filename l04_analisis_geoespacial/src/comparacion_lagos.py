"""Gráficos de evidencia para la sección 7 (comparación entre lagos).

Genera tres piezas de evidencia visual que sustentan las conclusiones de 7.4:
área de agua detectada por lago, distribución de cianobacteria por lago, y un
mapa de contexto geográfico con los poblados cercanos a cada lago.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd

from analisis_espacial import PROJECT_DIR, TEMPORAL_CSV

OUTPUT_DIR = PROJECT_DIR / "outputs" / "comparacion"
NOMBRES = {"atitlan": "Atitlán", "amatitlan": "Amatitlán"}
COLORES = {"atitlan": "#277DA1", "amatitlan": "#F3722C"}

# Sentinel-2 (bandas de 10 m): cada píxel válido representa 10 m x 10 m de superficie.
PIXEL_AREA_KM2 = (10 * 10) / 1_000_000

LAGO_ATITLAN = {
    "west": -91.326256, "east": -91.071510,
    "south": 14.594800, "north": 14.750979,
}
LAGO_AMATITLAN = {
    "west": -90.638065, "east": -90.512924,
    "south": 14.412347, "north": 14.493799,
}

# Coordenadas aproximadas de poblados conocidos alrededor de cada lago.
POBLADOS_CERCANOS = {
    "atitlan": [
        ("Panajachel", 14.7439, -91.1589),
        ("Sololá", 14.7724, -91.1831),
        ("Santiago Atitlán", 14.6386, -91.2339),
        ("San Pedro La Laguna", 14.6923, -91.2698),
    ],
    "amatitlan": [
        ("Amatitlán (cabecera)", 14.4776, -90.6157),
        ("Villa Nueva", 14.5266, -90.5866),
        ("Villa Canales", 14.4444, -90.5322),
    ],
}


def build_area_comparison(temporal: pd.DataFrame) -> Path:
    """Compara el área de agua detectada entre lagos, a partir de píxeles válidos."""
    resumen = (
        temporal.groupby("lago")["pixeles_validos"]
        .mean()
        .mul(PIXEL_AREA_KM2)
        .rename("area_km2")
        .reset_index()
    )
    resumen["lago_nombre"] = resumen["lago"].map(NOMBRES)

    figure, axis = plt.subplots(figsize=(6, 5))
    barras = axis.bar(
        resumen["lago_nombre"],
        resumen["area_km2"],
        color=[COLORES[lago] for lago in resumen["lago"]],
    )
    for barra, area in zip(barras, resumen["area_km2"]):
        axis.text(
            barra.get_x() + barra.get_width() / 2, area, f"{area:.1f} km²",
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )

    axis.set(
        title="Área de agua detectada por lago\n(promedio de píxeles válidos de las 11 fechas × 100 m² por píxel)",
        ylabel="Área (km²)",
    )
    figure.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "comparacion_area_lagos.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def build_boxplot_cianobacteria(temporal: pd.DataFrame) -> Path:
    """Boxplot del promedio de cianobacteria por lago (distribución de las 11 fechas)."""
    datos = [
        temporal.loc[temporal["lago"] == lago, "promedio_cyano"].values
        for lago in ("atitlan", "amatitlan")
    ]

    figure, axis = plt.subplots(figsize=(6, 5))
    caja = axis.boxplot(
        datos,
        labels=[NOMBRES["atitlan"], NOMBRES["amatitlan"]],
        patch_artist=True,
        widths=0.5,
    )
    for parche, lago in zip(caja["boxes"], ("atitlan", "amatitlan")):
        parche.set_facecolor(COLORES[lago])
        parche.set_alpha(0.6)

    axis.set(
        title="Distribución de cianobacteria estimada por lago\n(11 fechas oficiales cada uno)",
        ylabel="Promedio de clorofila-a estimada",
    )
    axis.grid(alpha=0.25, axis="y")
    figure.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "comparacion_boxplot_cianobacteria.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def build_location_map() -> Path:
    """Mapa estático (sin tiles de internet): bounding box y poblados cercanos por lago."""
    figure, axes = plt.subplots(1, 2, figsize=(13, 6))

    for axis, (lago, bbox) in zip(axes, (("atitlan", LAGO_ATITLAN), ("amatitlan", LAGO_AMATITLAN))):
        rectangulo = patches.Rectangle(
            (bbox["west"], bbox["south"]),
            bbox["east"] - bbox["west"],
            bbox["north"] - bbox["south"],
            linewidth=2, edgecolor=COLORES[lago], facecolor=COLORES[lago], alpha=0.25,
            label="Área de estudio (bounding box)",
        )
        axis.add_patch(rectangulo)

        for nombre_poblado, lat, lon in POBLADOS_CERCANOS[lago]:
            axis.scatter(lon, lat, color="black", zorder=5, s=25)
            axis.annotate(
                nombre_poblado, (lon, lat),
                textcoords="offset points", xytext=(5, 5), fontsize=8,
            )

        margen = 0.06
        axis.set_xlim(bbox["west"] - margen, bbox["east"] + margen)
        axis.set_ylim(bbox["south"] - margen, bbox["north"] + margen)
        axis.set_title(f"{NOMBRES[lago]}: ubicación y poblados cercanos")
        axis.set_xlabel("Longitud")
        axis.set_ylabel("Latitud")
        axis.set_aspect("equal")
        axis.grid(alpha=0.3)
        axis.legend(loc="lower right", fontsize=8)

    figure.suptitle("Contexto geográfico de los lagos estudiados", fontsize=13, fontweight="bold")
    figure.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "mapa_ubicacion_lagos.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def main() -> None:
    temporal = pd.read_csv(TEMPORAL_CSV, parse_dates=["fecha"])
    for constructor in (build_area_comparison, build_boxplot_cianobacteria):
        archivo = constructor(temporal)
        print(f"Gráfico generado: {archivo}")
    archivo_mapa = build_location_map()
    print(f"Gráfico generado: {archivo_mapa}")


if __name__ == "__main__":
    main()
