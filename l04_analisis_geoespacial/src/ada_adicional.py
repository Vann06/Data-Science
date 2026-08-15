"""Análisis exploratorio adicional (sección 8).

8.1: para cada fecha, ¿qué porcentaje del área de agua del lago tiene valores
"altos" de cianobacteria? A diferencia de la persistencia de la sección 5 (que usa
un umbral relativo por fecha —el percentil 90 de ESA fecha— y por construcción
siempre da ~10%), aquí el umbral se fija UNA VEZ con todos los píxeles de las 11
fechas del lago, para que el porcentaje sí varíe entre fechas y refleje la
extensión real de la floración en cada momento.

8.2: galería de un lago ordenada de la fecha con MENOS cianobacteria a la de MÁS
(no por orden cronológico). Con la misma escala de color en todas las imágenes,
permite ver si las zonas de acumulación ya son visibles desde las fechas más
leves (zona "semilla"/persistente que solo crece) o si aparecen en lugares
distintos según la fecha.

8.3: mapas de diferencia entre fechas consecutivas (orden cronológico) para un
lago: resta píxel a píxel de una fecha respecto a la anterior. A diferencia de
8.2 (severidad global de cada fecha), aquí el comparador es la fecha misma —
muestra DÓNDE aumentó o bajó la cianobacteria de una fecha a la siguiente, no
solo cuánto cambió el promedio.

8.4: estacionalidad. Una serie cronológica sola no distingue "estacional" de
"simplemente creciente con el tiempo" — para eso se necesita agrupar por MES
DEL AÑO, ignorando el año, y ver si el mismo mes se repite como pico en 2025 y
en 2026. Por eso el gráfico incluye ambas vistas: la serie cronológica pedida
y el promedio agrupado por mes.
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

OUTPUT_DIR = PROJECT_DIR / "outputs" / "eda_adicional"
NOMBRES = {"atitlan": "Atitlán", "amatitlan": "Amatitlán"}
COLORES = {"atitlan": "#277DA1", "amatitlan": "#F3722C"}
PERCENTIL_UMBRAL = 75  # "valores altos" = cuarto superior del propio historial del lago
MESES_ES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}


def extension_espacial(lake: str, temporal: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Calcula el % de píxeles de agua con cianobacteria alta, por fecha, para un lago."""
    serie = temporal.loc[temporal["lago"] == lake].sort_values("fecha")

    imagenes = {}
    todos_los_valores = []
    for row in serie.itertuples():
        fecha_str = row.fecha.strftime("%Y-%m-%d")
        data, _ = read_raster(lake, fecha_str)
        imagenes[fecha_str] = data
        todos_los_valores.append(data[np.isfinite(data)])

    umbral = float(np.percentile(np.concatenate(todos_los_valores), PERCENTIL_UMBRAL))

    filas = []
    for row in serie.itertuples():
        fecha_str = row.fecha.strftime("%Y-%m-%d")
        data = imagenes[fecha_str]
        validos = np.isfinite(data)
        altos = validos & (data >= umbral)
        filas.append({
            "lago": lake,
            "fecha": fecha_str,
            "porcentaje_area_alta": 100 * altos.sum() / validos.sum(),
        })

    return pd.DataFrame(filas), umbral


def build_extension_chart(temporal: pd.DataFrame) -> Path:
    """Grafica el % de área con cianobacteria alta por fecha, para ambos lagos."""
    figure, axis = plt.subplots(figsize=(12, 6))

    for lake in ("atitlan", "amatitlan"):
        resultado, umbral = extension_espacial(lake, temporal)
        resultado["fecha"] = pd.to_datetime(resultado["fecha"])
        axis.plot(
            resultado["fecha"], resultado["porcentaje_area_alta"],
            marker="o", linewidth=2.2, markersize=6,
            color=COLORES[lake],
            label=f"{NOMBRES[lake]} (umbral ≥ {umbral:.2f})",
        )

    axis.set(
        title=(
            "Extensión espacial de la floración por fecha\n"
            f"(% del área de agua con cianobacteria ≥ percentil {PERCENTIL_UMBRAL} del propio lago)"
        ),
        xlabel="Fecha",
        ylabel="% del área del lago con valores altos",
    )
    axis.legend(title="Lago")
    axis.grid(alpha=0.25)
    figure.autofmt_xdate(rotation=45)
    figure.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "extension_espacial_floracion.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def build_severity_gallery(lake: str, temporal: pd.DataFrame) -> Path:
    """Galería de un lago ordenada de menor a mayor cianobacteria (no por fecha).

    Complementa el mapa de persistencia de la sección 5.3: aquí se ve directamente
    si un punto del lago ya tiene color en las fechas más leves y solo se expande
    en las más severas (zona de acumulación persistente), en vez de aparecer y
    desaparecer sin patrón entre fechas.
    """
    serie = temporal.loc[temporal["lago"] == lake].sort_values("promedio_cyano").reset_index(drop=True)

    imagenes = []
    vmax_global = 0.0
    for row in serie.itertuples():
        fecha_str = row.fecha.strftime("%Y-%m-%d")
        data, _ = read_raster(lake, fecha_str)
        imagenes.append((fecha_str, row.promedio_cyano, data))
        vmax_global = max(vmax_global, np.nanpercentile(data, 99))

    total = len(imagenes)
    columnas = 4
    filas = -(-total // columnas)  # techo (ceil) sin usar math.ceil

    figure, axes = plt.subplots(
        filas, columnas,
        figsize=(3.2 * columnas, 3.4 * filas),
        squeeze=False,
    )

    for indice in range(filas * columnas):
        fila, columna = divmod(indice, columnas)
        axis = axes[fila][columna]
        axis.set_axis_off()
        if indice < total:
            fecha_str, promedio, data = imagenes[indice]
            axis.imshow(data, cmap="viridis", vmin=0, vmax=vmax_global)
            axis.set_title(f"{fecha_str}\nprom. {promedio:.2f}", fontsize=9)

    norm = Normalize(vmin=0, vmax=vmax_global)
    mappable = ScalarMappable(norm=norm, cmap="viridis")
    figure.colorbar(mappable, ax=axes, fraction=0.02, pad=0.02, label="Clorofila-a estimada")

    figure.suptitle(
        f"{NOMBRES[lake]}: mapas ordenados de menor a mayor cianobacteria (izq. a der., arriba a abajo)",
        fontsize=13, fontweight="bold",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / f"{lake}_galeria_severidad.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def build_difference_maps(lake: str, temporal: pd.DataFrame) -> Path:
    """Mapas de diferencia entre fechas consecutivas (orden cronológico) para un lago.

    Cada mapa es la resta píxel a píxel entre una fecha y la fecha oficial
    anterior: rojo = la cianobacteria subió en ese punto, azul = bajó. La escala
    de color es simétrica y compartida entre todos los mapas del lago, para que
    la intensidad de rojo/azul sea comparable entre pares de fechas.
    """
    serie = temporal.loc[temporal["lago"] == lake].sort_values("fecha").reset_index(drop=True)

    imagenes = []
    for row in serie.itertuples():
        fecha_str = row.fecha.strftime("%Y-%m-%d")
        data, _ = read_raster(lake, fecha_str)
        imagenes.append((fecha_str, data))

    diferencias = [
        (fecha_a, fecha_b, data_b - data_a)
        for (fecha_a, data_a), (fecha_b, data_b) in zip(imagenes[:-1], imagenes[1:])
    ]

    vmax_abs = max(np.nanpercentile(np.abs(diff), 99) for _, _, diff in diferencias)

    total = len(diferencias)
    columnas = 5
    filas = -(-total // columnas)  # techo (ceil) sin usar math.ceil

    figure, axes = plt.subplots(
        filas, columnas,
        figsize=(3.4 * columnas, 3.6 * filas),
        squeeze=False,
    )

    imagen_referencia = None
    for indice in range(filas * columnas):
        fila, columna = divmod(indice, columnas)
        axis = axes[fila][columna]
        axis.set_axis_off()
        if indice < total:
            fecha_a, fecha_b, diff = diferencias[indice]
            imagen_referencia = axis.imshow(diff, cmap="RdBu_r", vmin=-vmax_abs, vmax=vmax_abs)
            axis.set_title(f"{fecha_a} → {fecha_b}", fontsize=8)

    figure.colorbar(imagen_referencia, ax=axes, fraction=0.02, pad=0.02, label="Cambio en clorofila-a estimada")
    figure.suptitle(
        f"{NOMBRES[lake]}: mapas de diferencia entre fechas consecutivas\n(rojo = aumento, azul = disminución)",
        fontsize=13, fontweight="bold",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / f"{lake}_mapas_diferencia.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def build_seasonality_chart(temporal: pd.DataFrame) -> Path:
    """Serie cronológica + promedio por mes del año, para explorar estacionalidad.

    Panel izquierdo: tendencia en orden cronológico real (lo pedido literalmente).
    Panel derecho: las mismas observaciones agrupadas por mes del año (2025 y 2026
    combinados) — si un mes se repite como pico sin importar el año, es evidencia
    real de estacionalidad; una serie cronológica sola no permite distinguir eso
    de una tendencia que simplemente va en aumento.
    """
    figure, (axis_tiempo, axis_mes) = plt.subplots(1, 2, figsize=(16, 6))

    for lake in ("atitlan", "amatitlan"):
        serie = temporal.loc[temporal["lago"] == lake].sort_values("fecha")
        axis_tiempo.plot(
            serie["fecha"], serie["promedio_cyano"],
            marker="o", linewidth=2.2, markersize=6,
            color=COLORES[lake], label=NOMBRES[lake],
        )

    axis_tiempo.set(
        title="Serie cronológica (orden temporal real)",
        xlabel="Fecha", ylabel="Promedio de clorofila-a estimada",
    )
    axis_tiempo.legend(title="Lago")
    axis_tiempo.grid(alpha=0.25)
    axis_tiempo.tick_params(axis="x", rotation=45)

    con_mes = temporal.copy()
    con_mes["mes"] = con_mes["fecha"].dt.month
    promedio_mensual = con_mes.groupby(["lago", "mes"])["promedio_cyano"].mean()

    meses_presentes = sorted(con_mes["mes"].unique())
    posiciones = np.arange(len(meses_presentes))
    ancho = 0.35

    for desplazamiento, lake in zip((-ancho / 2, ancho / 2), ("atitlan", "amatitlan")):
        valores = [promedio_mensual.get((lake, mes), np.nan) for mes in meses_presentes]
        axis_mes.bar(posiciones + desplazamiento, valores, width=ancho, color=COLORES[lake], label=NOMBRES[lake])

    axis_mes.set(
        title="Promedio por mes del año (2025 y 2026 combinados)",
        xlabel="Mes", ylabel="Promedio de clorofila-a estimada",
    )
    axis_mes.set_xticks(posiciones)
    axis_mes.set_xticklabels([MESES_ES[mes] for mes in meses_presentes])
    axis_mes.legend(title="Lago")
    axis_mes.grid(alpha=0.25, axis="y")

    figure.suptitle("Exploración de estacionalidad en la cianobacteria estimada", fontsize=14, fontweight="bold")
    figure.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archivo = OUTPUT_DIR / "estacionalidad.png"
    figure.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close(figure)
    return archivo


def main() -> None:
    temporal = pd.read_csv(TEMPORAL_CSV, parse_dates=["fecha"])
    tablas = []
    for lake in ("atitlan", "amatitlan"):
        tabla, umbral = extension_espacial(lake, temporal)
        print(f"{NOMBRES[lake]}: umbral 'alto' (percentil {PERCENTIL_UMBRAL}) = {umbral:.3f}")
        tablas.append(tabla)
    resumen = pd.concat(tablas, ignore_index=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(OUTPUT_DIR / "extension_espacial_floracion.csv", index=False)

    archivo = build_extension_chart(temporal)
    print(f"Gráfico generado: {archivo}")

    for lake in ("atitlan", "amatitlan"):
        archivo_galeria = build_severity_gallery(lake, temporal)
        print(f"Galería generada: {archivo_galeria}")

    for lake in ("atitlan", "amatitlan"):
        archivo_diferencias = build_difference_maps(lake, temporal)
        print(f"Mapas de diferencia generados: {archivo_diferencias}")

    archivo_estacionalidad = build_seasonality_chart(temporal)
    print(f"Gráfico generado: {archivo_estacionalidad}")


if __name__ == "__main__":
    main()
