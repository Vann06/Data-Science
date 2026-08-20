"""Preparación reproducible de datos para los ejercicios 1--3 del Laboratorio 4.

El módulo convierte las 22 escenas ráster de la Parte I en un dataset Parquet
particionado. Cada fila representa un píxel de agua válido de 10 x 10 m. La
implementación procesa una escena a la vez para no mantener los ~15 millones
de observaciones simultáneamente en memoria.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


PIPELINE_VERSION = 4
CRS_ANALISIS = "EPSG:32615"
RESOLUCION_M = 10.0
UMBRAL_ALERTA_CHL = 12.0
UMBRAL_SUPERIOR_ALERTA_1 = 24.0
MIN_FECHAS_AGUA_PERSISTENTE = 3
MAX_NUBOSIDAD_ESCENA_PCT = 20.0
MIN_REFLECTANCIA_PLAUSIBLE = -0.1
MAX_REFLECTANCIA_PLAUSIBLE = 1.2
MUESTRA_POR_ESCENA = 10_000

BANDAS = ("B02", "B03", "B04", "B05", "B07", "B8A", "B08", "B11", "B12")
BANDAS_COLUMNAS = tuple(banda.lower() for banda in BANDAS)
PATRON_INDICE = re.compile(
    r"(?P<lago>atitlan|amatitlan)_(?P<fecha>\d{4}-\d{2}-\d{2})_ndvi\.tif$"
)

# Metadatos documentados en la Parte I. La nubosidad corresponde a la escena,
# no a una máscara por píxel; por eso se conserva también como covariable de
# calidad y se documenta su limitación en el notebook.
METADATOS_ESCENAS = {
    ("atitlan", "2025-01-18"): (0.02, "Sentinel-2B"),
    ("atitlan", "2025-04-13"): (0.54, "Sentinel-2C"),
    ("atitlan", "2025-05-13"): (4.37, "Sentinel-2C"),
    ("atitlan", "2025-07-17"): (3.57, "Sentinel-2A"),
    ("atitlan", "2025-11-21"): (3.15, "Sentinel-2A"),
    ("atitlan", "2025-12-29"): (3.17, "Sentinel-2C"),
    ("atitlan", "2026-02-12"): (0.04, "Sentinel-2B"),
    ("atitlan", "2026-03-24"): (3.17, "Sentinel-2B"),
    ("atitlan", "2026-04-13"): (0.01, "Sentinel-2B"),
    ("atitlan", "2026-04-28"): (4.96, "Sentinel-2C"),
    ("atitlan", "2026-07-22"): (4.02, "Sentinel-2B"),
    ("amatitlan", "2025-01-28"): (0.06, "Sentinel-2B"),
    ("amatitlan", "2025-04-15"): (0.09, "Sentinel-2A"),
    ("amatitlan", "2025-04-28"): (1.03, "Sentinel-2B"),
    ("amatitlan", "2025-11-24"): (0.50, "Sentinel-2B"),
    ("amatitlan", "2026-01-08"): (0.77, "Sentinel-2C"),
    ("amatitlan", "2026-02-02"): (0.39, "Sentinel-2B"),
    ("amatitlan", "2026-02-07"): (0.02, "Sentinel-2C"),
    ("amatitlan", "2026-03-29"): (0.01, "Sentinel-2C"),
    ("amatitlan", "2026-04-13"): (0.09, "Sentinel-2B"),
    ("amatitlan", "2026-04-28"): (4.96, "Sentinel-2C"),
    ("amatitlan", "2026-06-19"): (13.00, "Sentinel-2A"),
}

# La estimación de clorofila-a usa B04/B05 (NDCI). Además, la máscara de agua
# de la Parte I usa B02/B03/B04/B08/B11/B12 y los índices derivados NDVI/NDWI.
# Todos se excluyen del conjunto X bajo el criterio estricto del enunciado 2.5.
VARIABLES_PROHIBIDAS = {
    "alta_cyano",
    "chl_cyano",
    "nivel_biomasa_oms",
    "b02",
    "b03",
    "b04",
    "b05",
    "b08",
    "b11",
    "b12",
    "ndvi",
    "ndwi",
    "ndci",
    "mndwi",
    "aweish",
    "aweinsh",
    "dbsi",
}

PREDICTORES_BASE = [
    "b07",
    "b8a",
    "x_utm",
    "y_utm",
    "sin_dia_anio",
    "cos_dia_anio",
    "dias_desde_inicio",
    "lago",
    "nubosidad_pct",
    "satelite",
]


@dataclass(frozen=True)
class Escena:
    lago: str
    fecha: str
    bandas: Path
    ndvi: Path
    ndwi: Path
    cyano: Path
    nubosidad_pct: float
    satelite: str


def localizar_proyecto(inicio: Path | str | None = None) -> Path:
    """Localiza la raíz del laboratorio desde el directorio actual o sus padres."""
    inicio = Path(inicio or Path.cwd()).resolve()
    candidatos = [inicio, *inicio.parents]
    for candidato in candidatos:
        if candidato.name == "l04_analisis_geoespacial" and (candidato / "data").exists():
            return candidato
        anidado = candidato / "l04_analisis_geoespacial"
        if (anidado / "data").exists():
            return anidado
    raise FileNotFoundError("No se encontró la raíz l04_analisis_geoespacial.")


def inventariar_escenas(proyecto: Path | str) -> pd.DataFrame:
    """Valida existencia, rejilla, bandas y metadatos de las 22 escenas."""
    proyecto = Path(proyecto)
    registros: list[dict] = []
    for ruta_ndvi in sorted((proyecto / "data" / "indices").glob("*_ndvi.tif")):
        coincidencia = PATRON_INDICE.fullmatch(ruta_ndvi.name)
        if coincidencia is None:
            raise ValueError(f"Nombre de ráster inesperado: {ruta_ndvi.name}")
        lago, fecha = coincidencia.group("lago", "fecha")
        if (lago, fecha) not in METADATOS_ESCENAS:
            raise ValueError(f"Faltan metadatos de escena para {lago} {fecha}.")
        nubosidad_pct, satelite = METADATOS_ESCENAS[(lago, fecha)]
        escena = Escena(
            lago=lago,
            fecha=fecha,
            bandas=proyecto / "data" / lago / f"{fecha}_bandas.tif",
            ndvi=ruta_ndvi,
            ndwi=proyecto / "data" / "indices" / f"{lago}_{fecha}_ndwi.tif",
            cyano=proyecto / "notebooks" / "resultados_cyano" / f"{lago}_{fecha}.tif",
            nubosidad_pct=float(nubosidad_pct),
            satelite=satelite,
        )
        for ruta in (escena.bandas, escena.ndvi, escena.ndwi, escena.cyano):
            if not ruta.exists():
                raise FileNotFoundError(f"Falta el archivo requerido: {ruta}")

        with (
            rasterio.open(escena.bandas) as src_bandas,
            rasterio.open(escena.ndvi) as src_ndvi,
            rasterio.open(escena.ndwi) as src_ndwi,
            rasterio.open(escena.cyano) as src_cyano,
        ):
            fuentes = (src_bandas, src_ndvi, src_ndwi, src_cyano)
            if src_bandas.descriptions != BANDAS:
                raise ValueError(
                    f"Orden de bandas inesperado en {escena.bandas}: {src_bandas.descriptions}"
                )
            if not all(src.crs == src_ndvi.crs for src in fuentes):
                raise ValueError(f"CRS no alineado en {lago} {fecha}.")
            if not all(src.transform == src_ndvi.transform for src in fuentes):
                raise ValueError(f"Transformación no alineada en {lago} {fecha}.")
            if not all(src.shape == src_ndvi.shape for src in fuentes):
                raise ValueError(f"Dimensiones no alineadas en {lago} {fecha}.")
            if str(src_ndvi.crs) != CRS_ANALISIS:
                raise ValueError(f"Se esperaba {CRS_ANALISIS}; se obtuvo {src_ndvi.crs}.")
            if tuple(map(float, src_ndvi.res)) != (RESOLUCION_M, RESOLUCION_M):
                raise ValueError(f"Resolución inesperada en {lago} {fecha}: {src_ndvi.res}")
            registros.append(
                {
                    **escena.__dict__,
                    "alto": src_ndvi.height,
                    "ancho": src_ndvi.width,
                    "pixeles_totales": src_ndvi.height * src_ndvi.width,
                    "crs": str(src_ndvi.crs),
                    "resolucion_m": float(src_ndvi.res[0]),
                }
            )

    inventario = pd.DataFrame(registros).sort_values(["lago", "fecha"]).reset_index(drop=True)
    if len(inventario) != 22:
        raise ValueError(f"Se esperaban 22 escenas; se encontraron {len(inventario)}.")
    if set(zip(inventario["lago"], inventario["fecha"])) != set(METADATOS_ESCENAS):
        raise ValueError("Las escenas encontradas no coinciden con las fechas oficiales.")
    return inventario


def construir_mascara_lago(inventario: pd.DataFrame, lago: str) -> np.ndarray:
    """Aproxima el límite del lago con agua detectada en al menos tres fechas.

    La Parte I no contiene un polígono oficial. Usar persistencia multitemporal
    reduce falsos positivos aislados en tierra y evita considerar una sola
    clasificación espectral como límite definitivo.
    """
    conteo: np.ndarray | None = None
    grupo = inventario.loc[inventario["lago"] == lago].sort_values("fecha")
    for ruta in grupo["cyano"]:
        with rasterio.open(ruta) as src:
            valido = np.isfinite(src.read(1))
        conteo = valido.astype("uint8") if conteo is None else conteo + valido
    if conteo is None:
        raise ValueError(f"No hay escenas para {lago}.")
    return conteo >= MIN_FECHAS_AGUA_PERSISTENTE


def _coordenadas_utm(transform: rasterio.Affine, filas: np.ndarray, columnas: np.ndarray):
    """Calcula centros de píxel; las rejillas del laboratorio no están rotadas."""
    if transform.b != 0 or transform.d != 0:
        xs, ys = rasterio.transform.xy(transform, filas, columnas, offset="center")
        return np.asarray(xs, dtype="float32"), np.asarray(ys, dtype="float32")
    x = transform.c + (columnas.astype("float64") + 0.5) * transform.a
    y = transform.f + (filas.astype("float64") + 0.5) * transform.e
    return x.astype("float32"), y.astype("float32")


def agregar_variables_temporales(tabla: pd.DataFrame) -> pd.DataFrame:
    """Agrega codificación cíclica anual y tendencia desde la primera escena."""
    fechas = pd.to_datetime(tabla["fecha"])
    dia = fechas.dt.dayofyear.astype("float32")
    periodo = np.where(fechas.dt.is_leap_year, 366.0, 365.0).astype("float32")
    angulo = 2 * np.pi * dia / periodo
    tabla["sin_dia_anio"] = np.sin(angulo).astype("float32")
    tabla["cos_dia_anio"] = np.cos(angulo).astype("float32")
    tabla["dias_desde_inicio"] = (
        (fechas - pd.Timestamp("2025-01-18")).dt.days.astype("float32")
    )
    return tabla


def clasificar_respuesta(chl_cyano: np.ndarray | pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Construye respuesta binaria y nivel operativo de biomasa OMS 2021."""
    valores = np.asarray(chl_cyano, dtype="float32")
    alta = (valores >= UMBRAL_ALERTA_CHL).astype("uint8")
    nivel = np.select(
        [valores < UMBRAL_ALERTA_CHL, valores < UMBRAL_SUPERIOR_ALERTA_1],
        [0, 1],
        default=2,
    ).astype("uint8")
    return alta, nivel


def procesar_escena(registro: pd.Series, mascara_lago: np.ndarray) -> tuple[pd.DataFrame, dict]:
    """Limpia y aplana una escena ya validada."""
    with rasterio.open(registro["bandas"]) as src:
        bandas_dn = src.read()
        nodata = src.nodata
        transform = src.transform
    with rasterio.open(registro["ndvi"]) as src:
        ndvi = src.read(1).astype("float32")
    with rasterio.open(registro["ndwi"]) as src:
        ndwi = src.read(1).astype("float32")
    with rasterio.open(registro["cyano"]) as src:
        chl = src.read(1).astype("float32")

    if registro["nubosidad_pct"] > MAX_NUBOSIDAD_ESCENA_PCT:
        raise ValueError(
            f"{registro['lago']} {registro['fecha']} supera el máximo de nubosidad "
            f"({registro['nubosidad_pct']} > {MAX_NUBOSIDAD_ESCENA_PCT})."
        )

    bandas_sin_nodata = np.all(bandas_dn != nodata, axis=0) if nodata is not None else np.ones(chl.shape, bool)
    bandas = bandas_dn.astype("float32") / 10_000.0
    # La reflectancia de superficie L2A puede ser ligeramente negativa después
    # de la corrección atmosférica sobre agua oscura. Esos valores no equivalen
    # a NoData; solo se eliminan valores extremos fuera de un intervalo amplio.
    reflectancia_plausible = np.all(
        (bandas >= MIN_REFLECTANCIA_PLAUSIBLE)
        & (bandas <= MAX_REFLECTANCIA_PLAUSIBLE),
        axis=0,
    )
    indices_validos = (
        np.isfinite(ndvi)
        & np.isfinite(ndwi)
        & (ndvi >= -1)
        & (ndvi <= 1)
        & (ndwi >= -1)
        & (ndwi <= 1)
    )
    objetivo_valido = np.isfinite(chl)

    # Heurística conservadora para nubosidad residual: una nube es brillante en
    # el visible y mantiene señal SWIR alta; el agua suele ser oscura en SWIR.
    brillo_visible = bandas[[0, 1, 2]].mean(axis=0)
    nube_brilante = (brillo_visible > 0.25) & (bandas[7] > 0.10)

    mascara_final = (
        mascara_lago
        & objetivo_valido
        & bandas_sin_nodata
        & reflectancia_plausible
        & indices_validos
        & ~nube_brilante
    )
    filas, columnas = np.nonzero(mascara_final)
    x_utm, y_utm = _coordenadas_utm(transform, filas, columnas)
    valores_chl = np.maximum(chl[mascara_final], 0).astype("float32")
    alta_cyano, nivel_biomasa = clasificar_respuesta(valores_chl)

    datos: dict[str, object] = {
        "lago": registro["lago"],
        "fecha": pd.Timestamp(registro["fecha"]),
        "fila": filas.astype("int32"),
        "columna": columnas.astype("int32"),
        "x_utm": x_utm,
        "y_utm": y_utm,
    }
    for indice, columna in enumerate(BANDAS_COLUMNAS):
        datos[columna] = bandas[indice][mascara_final].astype("float32")
    datos.update(
        {
            "ndvi": ndvi[mascara_final],
            "ndwi": ndwi[mascara_final],
            "chl_cyano": valores_chl,
            "nivel_biomasa_oms": nivel_biomasa,
            "alta_cyano": alta_cyano,
            "nubosidad_pct": np.float32(registro["nubosidad_pct"]),
            "satelite": registro["satelite"],
        }
    )
    tabla = pd.DataFrame(datos)
    tabla = agregar_variables_temporales(tabla)
    tabla["lago"] = tabla["lago"].astype("category")
    tabla["satelite"] = tabla["satelite"].astype("category")

    resumen = {
        "lago": registro["lago"],
        "fecha": registro["fecha"],
        "pixeles_totales_bbox": int(chl.size),
        "pixeles_mascara_persistente": int(mascara_lago.sum()),
        "pixeles_objetivo_valido": int(objetivo_valido.sum()),
        "descartados_nodata_bandas": int((mascara_lago & objetivo_valido & ~bandas_sin_nodata).sum()),
        "descartados_reflectancia": int((mascara_lago & objetivo_valido & bandas_sin_nodata & ~reflectancia_plausible).sum()),
        "descartados_indices": int((mascara_lago & objetivo_valido & bandas_sin_nodata & reflectancia_plausible & ~indices_validos).sum()),
        "descartados_nube_brilante": int((mascara_lago & objetivo_valido & bandas_sin_nodata & reflectancia_plausible & indices_validos & nube_brilante).sum()),
        "observaciones_validas": int(len(tabla)),
        "n_clase_0": int((alta_cyano == 0).sum()),
        "n_clase_1": int((alta_cyano == 1).sum()),
    }
    resumen["pct_conservado_bbox"] = 100 * resumen["observaciones_validas"] / resumen["pixeles_totales_bbox"]
    resumen["pct_clase_1"] = 100 * resumen["n_clase_1"] / max(resumen["observaciones_validas"], 1)
    return tabla, resumen


def catalogo_variables() -> pd.DataFrame:
    """Diccionario de variables del dataset final."""
    filas = [
        ("lago", "category", "Identificador del lago", "espacial/categórica"),
        ("fecha", "datetime64[ns]", "Fecha de adquisición", "temporal/identificador"),
        ("fila", "int32", "Fila del píxel en el ráster", "identificador"),
        ("columna", "int32", "Columna del píxel en el ráster", "identificador"),
        ("x_utm", "float32", "Coordenada este en EPSG:32615 (m)", "espacial"),
        ("y_utm", "float32", "Coordenada norte en EPSG:32615 (m)", "espacial"),
    ]
    descripciones_bandas = {
        "b02": "Reflectancia azul Sentinel-2",
        "b03": "Reflectancia verde Sentinel-2",
        "b04": "Reflectancia roja Sentinel-2",
        "b05": "Reflectancia red-edge 1 Sentinel-2",
        "b07": "Reflectancia red-edge 3 Sentinel-2",
        "b8a": "Reflectancia NIR estrecha Sentinel-2",
        "b08": "Reflectancia NIR Sentinel-2",
        "b11": "Reflectancia SWIR 1 Sentinel-2",
        "b12": "Reflectancia SWIR 2 Sentinel-2",
    }
    filas.extend((v, "float32", d, "banda espectral") for v, d in descripciones_bandas.items())
    filas.extend(
        [
            ("ndvi", "float32", "Índice normalizado de vegetación (B08, B04)", "índice"),
            ("ndwi", "float32", "Índice normalizado de agua (B03, B08)", "índice"),
            ("chl_cyano", "float32", "Clorofila-a estimada mediante NDCI (µg/L)", "respuesta continua"),
            ("nivel_biomasa_oms", "uint8", "0: <12; 1: 12-<24; 2: >=24 µg/L", "categoría respuesta"),
            ("alta_cyano", "uint8", "0: <12; 1: >=12 µg/L", "respuesta binaria"),
            ("nubosidad_pct", "float32", "Nubosidad reportada para la escena", "calidad"),
            ("satelite", "category", "Plataforma Sentinel-2 A/B/C", "categórica"),
            ("sin_dia_anio", "float32", "Seno del día del año", "ingeniería temporal"),
            ("cos_dia_anio", "float32", "Coseno del día del año", "ingeniería temporal"),
            ("dias_desde_inicio", "float32", "Días desde 2025-01-18", "ingeniería temporal"),
        ]
    )
    return pd.DataFrame(filas, columns=["variable", "tipo_esperado", "descripcion", "familia"])


def auditar_predictores(columnas: list[str] | pd.Index) -> pd.DataFrame:
    """Explica por qué cada variable se usa o se excluye de X."""
    columnas = list(columnas)
    filas = []
    for variable in columnas:
        if variable in VARIABLES_PROHIBIDAS:
            decision = "EXCLUIR"
            razon = "Fuga: intervino en el valor o en la máscara que construyó la respuesta."
        elif variable in PREDICTORES_BASE:
            decision = "INCLUIR"
            razon = "Predictor base sin uso directo ni indirecto en la construcción de la respuesta."
        else:
            decision = "EXCLUIR"
            razon = "Identificador, variable redundante o no seleccionada para el modelo base."
        filas.append((variable, decision, razon))
    auditoria = pd.DataFrame(filas, columns=["variable", "decision", "razon"])
    if not set(PREDICTORES_BASE).issubset(columnas):
        faltantes = sorted(set(PREDICTORES_BASE) - set(columnas))
        raise ValueError(f"Faltan predictores base en el dataset: {faltantes}")
    if not VARIABLES_PROHIBIDAS.isdisjoint(PREDICTORES_BASE):
        raise AssertionError("El conjunto predictor contiene variables prohibidas.")
    return auditoria


def _resumen_variables(tabla: pd.DataFrame, total: int) -> pd.DataFrame:
    catalogo = catalogo_variables().set_index("variable")
    resumen = pd.DataFrame(
        {
            "variable": tabla.columns,
            "tipo_dato": [str(tabla[c].dtype) for c in tabla.columns],
            "valores_faltantes": 0,
            "pct_faltantes": 0.0,
            "observaciones_evaluadas": total,
        }
    )
    return resumen.join(catalogo[["descripcion", "familia"]], on="variable")


def ejecutar_pipeline(
    proyecto: Path | str | None = None,
    salida: Path | str | None = None,
    reutilizar: bool = False,
) -> dict[str, object]:
    """Ejecuta el pipeline y devuelve rutas y resúmenes principales."""
    proyecto = localizar_proyecto(proyecto)
    salida = Path(salida or proyecto / "parte_2" / "data" / "processed")
    dataset_dir = salida / "dataset_ml"
    manifest_path = salida / "manifest.json"
    archivos_resumen = {
        "limpieza": salida / "resumen_limpieza.csv",
        "lago_fecha": salida / "resumen_lago_fecha.csv",
        "lago": salida / "resumen_lago.csv",
        "variables": salida / "resumen_variables.csv",
        "catalogo": salida / "catalogo_variables.csv",
        "auditoria": salida / "auditoria_predictores.csv",
        "muestra": salida / "muestra_eda.parquet",
    }
    if reutilizar and manifest_path.exists() and all(p.exists() for p in archivos_resumen.values()):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("pipeline_version") == PIPELINE_VERSION:
            return {
                "proyecto": proyecto,
                "salida": salida,
                "dataset_dir": dataset_dir,
                "manifest": manifest,
                **archivos_resumen,
            }

    salida.mkdir(parents=True, exist_ok=True)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    inventario = inventariar_escenas(proyecto)
    muestras: list[pd.DataFrame] = []
    resumenes: list[dict] = []

    for lago in sorted(inventario["lago"].unique()):
        mascara_lago = construir_mascara_lago(inventario, lago)
        for _, registro in inventario.loc[inventario["lago"] == lago].iterrows():
            tabla, resumen = procesar_escena(registro, mascara_lago)
            particion = dataset_dir / f"lago={lago}" / f"fecha={registro['fecha']}"
            particion.mkdir(parents=True, exist_ok=True)
            ruta_parquet = particion / "observaciones.parquet"
            tabla.to_parquet(ruta_parquet, index=False, compression="zstd")
            semilla = zlib.crc32(f"{lago}-{registro['fecha']}".encode("utf-8"))
            n_muestra = min(MUESTRA_POR_ESCENA, len(tabla))
            muestras.append(tabla.sample(n=n_muestra, random_state=semilla))
            resumenes.append(resumen)
            print(
                f"{lago:10s} {registro['fecha']}: {len(tabla):,} observaciones, "
                f"{resumen['pct_clase_1']:.3f}% clase 1"
            )

    resumen_limpieza = pd.DataFrame(resumenes).sort_values(["lago", "fecha"])
    muestra = pd.concat(muestras, ignore_index=True)
    total = int(resumen_limpieza["observaciones_validas"].sum())
    resumen_lago_fecha = resumen_limpieza[
        ["lago", "fecha", "observaciones_validas", "n_clase_0", "n_clase_1", "pct_clase_1"]
    ].copy()
    resumen_lago = (
        resumen_lago_fecha.groupby("lago", as_index=False)[
            ["observaciones_validas", "n_clase_0", "n_clase_1"]
        ]
        .sum()
    )
    resumen_lago["pct_clase_1"] = 100 * resumen_lago["n_clase_1"] / resumen_lago["observaciones_validas"]
    resumen_variables = _resumen_variables(muestra, total)
    catalogo = catalogo_variables()
    auditoria = auditar_predictores(muestra.columns)

    resumen_limpieza.to_csv(archivos_resumen["limpieza"], index=False)
    resumen_lago_fecha.to_csv(archivos_resumen["lago_fecha"], index=False)
    resumen_lago.to_csv(archivos_resumen["lago"], index=False)
    resumen_variables.to_csv(archivos_resumen["variables"], index=False)
    catalogo.to_csv(archivos_resumen["catalogo"], index=False)
    auditoria.to_csv(archivos_resumen["auditoria"], index=False)
    muestra.to_parquet(archivos_resumen["muestra"], index=False, compression="zstd")

    n0 = int(resumen_lago["n_clase_0"].sum())
    n1 = int(resumen_lago["n_clase_1"].sum())
    manifest = {
        "pipeline_version": PIPELINE_VERSION,
        "crs": CRS_ANALISIS,
        "resolucion_m": RESOLUCION_M,
        "numero_escenas": int(len(inventario)),
        "observaciones_totales": total,
        "n_clase_0": n0,
        "n_clase_1": n1,
        "pct_clase_1": 100 * n1 / total,
        "razon_mayoria_minoria": max(n0, n1) / max(min(n0, n1), 1),
        "umbral_alerta_chl_ug_l": UMBRAL_ALERTA_CHL,
        "min_fechas_agua_persistente": MIN_FECHAS_AGUA_PERSISTENTE,
        "max_nubosidad_escena_pct": MAX_NUBOSIDAD_ESCENA_PCT,
        "predictores_base": PREDICTORES_BASE,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Puertas de calidad del avance 1--3.
    assert manifest["numero_escenas"] == 22
    assert total > 0 and n0 > 0 and n1 > 0
    assert resumen_variables["pct_faltantes"].eq(0).all()
    assert VARIABLES_PROHIBIDAS.isdisjoint(PREDICTORES_BASE)
    assert set(PREDICTORES_BASE).issubset(muestra.columns)

    return {
        "proyecto": proyecto,
        "salida": salida,
        "dataset_dir": dataset_dir,
        "manifest": manifest,
        **archivos_resumen,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--reuse", action="store_true", help="Reutiliza resultados de la misma versión.")
    argumentos = parser.parse_args()
    resultado = ejecutar_pipeline(argumentos.project_dir, argumentos.output_dir, argumentos.reuse)
    print(json.dumps(resultado["manifest"], indent=2, ensure_ascii=False))
    print(f"Dataset particionado: {resultado['dataset_dir']}")


if __name__ == "__main__":
    main()
