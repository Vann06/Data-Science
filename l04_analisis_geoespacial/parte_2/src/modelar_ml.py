"""Modelado convencional y evaluación para los ejercicios 4 y 5.

El módulo crea una muestra proporcional reproducible del dataset particionado,
mantiene una única división estratificada 70/30 y ajusta tres clasificadores:
regresión logística, Random Forest y XGBoost. Los hiperparámetros
se seleccionan únicamente con una validación interna del conjunto de
entrenamiento; el test permanece intacto hasta la comparación final.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zlib
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from preparar_ml import PREDICTORES_BASE, VARIABLES_PROHIBIDAS, ejecutar_pipeline, localizar_proyecto


MODELING_VERSION = 3
RANDOM_STATE = 42
N_MUESTRA_MODELADO = 600_000
TEST_SIZE = 0.30
VALIDATION_SIZE_WITHIN_TRAIN = 0.20

OBJETIVO = "alta_cyano"
NUMERICAS = [
    "b07",
    "b8a",
    "x_utm",
    "y_utm",
    "sin_dia_anio",
    "cos_dia_anio",
    "dias_desde_inicio",
    "nubosidad_pct",
]
CATEGORICAS = ["lago", "satelite"]
PREDICTORAS = list(PREDICTORES_BASE)

# Ablación para detectar cuánto depende el resultado de ubicación y metadatos
# de escena. No reemplaza la validación espacial solicitada en el ejercicio 6.
PREDICTORAS_SIN_ATAJOS = [
    "b07",
    "b8a",
    "sin_dia_anio",
    "cos_dia_anio",
    "dias_desde_inicio",
]

CONFIGURACIONES = {
    "Regresión Logística": [
        {"C": 0.1},
        {"C": 1.0},
        {"C": 10.0},
    ],
    "Random Forest": [
        {"n_estimators": 160, "max_depth": 14, "min_samples_leaf": 5, "max_features": "sqrt"},
        {"n_estimators": 240, "max_depth": 20, "min_samples_leaf": 3, "max_features": "sqrt"},
        {"n_estimators": 240, "max_depth": None, "min_samples_leaf": 10, "max_features": 0.7},
    ],
    "XGBoost": [
        {"n_estimators": 220, "max_depth": 4, "learning_rate": 0.05, "min_child_weight": 3, "subsample": 0.85, "colsample_bytree": 0.85},
        {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.05, "min_child_weight": 2, "subsample": 0.90, "colsample_bytree": 0.90},
        {"n_estimators": 260, "max_depth": 6, "learning_rate": 0.08, "min_child_weight": 5, "subsample": 0.85, "colsample_bytree": 0.80},
    ],
}


def _asignar_tamanios(resumen: pd.DataFrame, total_muestra: int) -> np.ndarray:
    """Distribuye el tamaño muestral proporcionalmente y conserva el total exacto."""
    pesos = resumen["observaciones_validas"].to_numpy(dtype="float64")
    cuotas = total_muestra * pesos / pesos.sum()
    tamanios = np.floor(cuotas).astype(int)
    faltan = total_muestra - tamanios.sum()
    if faltan:
        orden = np.argsort(-(cuotas - tamanios))
        tamanios[orden[:faltan]] += 1
    if np.any(tamanios > pesos):
        raise ValueError("La muestra solicitada excede alguna partición.")
    return tamanios


def construir_muestra_modelado(resultado_prep: dict, ruta: Path, reutilizar: bool = True) -> pd.DataFrame:
    """Muestrea cada escena en proporción a su número de píxeles válidos."""
    if reutilizar and ruta.exists():
        datos = pd.read_parquet(ruta)
        if len(datos) == N_MUESTRA_MODELADO and "particion" in datos:
            return datos

    resumen = pd.read_csv(resultado_prep["lago_fecha"])
    resumen["n_muestra"] = _asignar_tamanios(resumen, N_MUESTRA_MODELADO)
    fragmentos: list[pd.DataFrame] = []
    columnas = [*PREDICTORAS, OBJETIVO, "fecha", "fila", "columna"]

    for fila in resumen.itertuples(index=False):
        archivo = (
            Path(resultado_prep["dataset_dir"])
            / f"lago={fila.lago}"
            / f"fecha={fila.fecha}"
            / "observaciones.parquet"
        )
        escena = pd.read_parquet(archivo, columns=columnas)
        semilla = zlib.crc32(f"modelo-{fila.lago}-{fila.fecha}".encode("utf-8"))
        fragmentos.append(escena.sample(n=int(fila.n_muestra), random_state=semilla))

    datos = pd.concat(fragmentos, ignore_index=True)
    if len(datos) != N_MUESTRA_MODELADO:
        raise AssertionError("La muestra de modelado no tiene el tamaño esperado.")
    if datos[PREDICTORAS + [OBJETIVO]].isna().any().any():
        raise AssertionError("La muestra de modelado contiene valores faltantes.")
    if not VARIABLES_PROHIBIDAS.isdisjoint(PREDICTORAS):
        raise AssertionError("Se detectó fuga de información en los predictores.")
    if set(PREDICTORAS) != set(NUMERICAS + CATEGORICAS):
        raise AssertionError("El modelado no usa exactamente el conjunto definido en el ejercicio 3.")

    indices = np.arange(len(datos))
    idx_train, idx_test = train_test_split(
        indices,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=datos[OBJETIVO],
    )
    datos["particion"] = "train"
    datos.loc[idx_test, "particion"] = "test"
    datos["particion"] = datos["particion"].astype("category")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos.to_parquet(ruta, index=False, compression="zstd")
    return datos


def _preprocesador(escalar: bool, denso: bool = True) -> ColumnTransformer:
    numerico = StandardScaler() if escalar else "passthrough"
    categorico = OneHotEncoder(handle_unknown="ignore", sparse_output=not denso)
    return ColumnTransformer(
        [("num", numerico, NUMERICAS), ("cat", categorico, CATEGORICAS)],
        remainder="drop",
        sparse_threshold=0.0 if denso else 0.3,
    )


def _estimador(nombre: str, parametros: dict) -> Pipeline:
    if nombre == "Regresión Logística":
        modelo = LogisticRegression(
            **parametros,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=600,
            random_state=RANDOM_STATE,
        )
        return Pipeline([("pre", _preprocesador(escalar=True)), ("modelo", modelo)])
    if nombre == "Random Forest":
        modelo = RandomForestClassifier(
            **parametros,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
        return Pipeline([("pre", _preprocesador(escalar=False)), ("modelo", modelo)])
    if nombre == "XGBoost":
        modelo = XGBClassifier(
            **parametros,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            scale_pos_weight=98.7,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
        return Pipeline([("pre", _preprocesador(escalar=False)), ("modelo", modelo)])
    raise KeyError(nombre)


def umbral_f2(y_true: pd.Series | np.ndarray, probabilidades: np.ndarray) -> tuple[float, float]:
    """Selecciona en validación el umbral que maximiza F2 (recall pesa 4x)."""
    precision, recall, thresholds = precision_recall_curve(y_true, probabilidades)
    if not len(thresholds):
        return 0.5, 0.0
    p, r = precision[:-1], recall[:-1]
    f2 = np.divide(5 * p * r, 4 * p + r, out=np.zeros_like(p), where=(4 * p + r) > 0)
    mejor = int(np.nanargmax(f2))
    return float(thresholds[mejor]), float(f2[mejor])


def metricas_binarias(
    y_true: pd.Series | np.ndarray,
    probabilidades: np.ndarray,
    umbral: float,
) -> tuple[dict, np.ndarray]:
    prediccion = (probabilidades >= umbral).astype("uint8")
    matriz = confusion_matrix(y_true, prediccion, labels=[0, 1])
    tn, fp, fn, tp = matriz.ravel()
    metricas = {
        "umbral": float(umbral),
        "accuracy": accuracy_score(y_true, prediccion),
        "precision": precision_score(y_true, prediccion, zero_division=0),
        "recall": recall_score(y_true, prediccion, zero_division=0),
        "f1": f1_score(y_true, prediccion, zero_division=0),
        "f2": fbeta_score(y_true, prediccion, beta=2, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probabilidades),
        "pr_auc": average_precision_score(y_true, probabilidades),
        "balanced_accuracy": balanced_accuracy_score(y_true, prediccion),
        "specificity": tn / max(tn + fp, 1),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
    return metricas, matriz


def _hash_test(datos_test: pd.DataFrame) -> str:
    claves = (
        datos_test[["lago", "fecha", "fila", "columna"]]
        .astype(str)
        .agg("|".join, axis=1)
        .sort_values()
        .str.cat(sep="\n")
    )
    return hashlib.sha256(claves.encode("utf-8")).hexdigest()


def ejecutar_modelos(
    proyecto: Path | str | None = None,
    salida: Path | str | None = None,
    reutilizar: bool = False,
) -> dict:
    proyecto = localizar_proyecto(proyecto)
    resultado_prep = ejecutar_pipeline(proyecto, reutilizar=True)
    salida = Path(salida or proyecto / "parte_2" / "data" / "processed" / "modelos")
    salida.mkdir(parents=True, exist_ok=True)
    modelos_dir = salida / "estimadores"
    modelos_dir.mkdir(parents=True, exist_ok=True)

    rutas = {
        "muestra": salida / "muestra_modelado.parquet",
        "busqueda": salida / "busqueda_hiperparametros.csv",
        "metricas_05": salida / "metricas_umbral_05.csv",
        "metricas_operativas": salida / "metricas_umbral_operativo.csv",
        "predicciones": salida / "predicciones_test.parquet",
        "manifest": salida / "manifest_modelos.json",
    }
    if reutilizar and all(ruta.exists() for ruta in rutas.values()):
        manifest = json.loads(rutas["manifest"].read_text(encoding="utf-8"))
        if manifest.get("modeling_version") == MODELING_VERSION:
            return {"salida": salida, **rutas, "manifest_data": manifest}

    datos = construir_muestra_modelado(resultado_prep, rutas["muestra"], reutilizar=reutilizar)
    train = datos.loc[datos["particion"] == "train"].copy()
    test = datos.loc[datos["particion"] == "test"].copy()
    X_train, y_train = train[PREDICTORAS], train[OBJETIVO].astype("uint8")
    X_test, y_test = test[PREDICTORAS], test[OBJETIVO].astype("uint8")

    idx_ajuste, idx_validacion = train_test_split(
        np.arange(len(train)),
        test_size=VALIDATION_SIZE_WITHIN_TRAIN,
        random_state=RANDOM_STATE,
        stratify=y_train,
    )
    X_ajuste, y_ajuste = X_train.iloc[idx_ajuste], y_train.iloc[idx_ajuste]
    X_validacion, y_validacion = X_train.iloc[idx_validacion], y_train.iloc[idx_validacion]

    filas_busqueda: list[dict] = []
    metricas_05: list[dict] = []
    metricas_operativas: list[dict] = []
    predicciones = test[["lago", "fecha", "fila", "columna", OBJETIVO]].reset_index(drop=True)
    umbrales: dict[str, float] = {}
    parametros_elegidos: dict[str, dict] = {}

    for nombre, configuraciones in CONFIGURACIONES.items():
        mejor = None
        for numero, parametros in enumerate(configuraciones, start=1):
            estimador = _estimador(nombre, parametros)
            inicio = time.perf_counter()
            estimador.fit(X_ajuste, y_ajuste)
            segundos = time.perf_counter() - inicio
            prob_val = estimador.predict_proba(X_validacion)[:, 1]
            pr_auc = average_precision_score(y_validacion, prob_val)
            roc_auc = roc_auc_score(y_validacion, prob_val)
            threshold, f2_val = umbral_f2(y_validacion, prob_val)
            registro = {
                "modelo": nombre,
                "configuracion": numero,
                "parametros": json.dumps(parametros, ensure_ascii=False, sort_keys=True),
                "pr_auc_validacion": pr_auc,
                "roc_auc_validacion": roc_auc,
                "f2_validacion": f2_val,
                "umbral_f2_validacion": threshold,
                "segundos_ajuste": segundos,
            }
            filas_busqueda.append(registro)
            if mejor is None or (pr_auc, f2_val) > (mejor["pr_auc"], mejor["f2"]):
                mejor = {
                    "pr_auc": pr_auc,
                    "f2": f2_val,
                    "umbral": threshold,
                    "parametros": parametros,
                }
            print(
                f"{nombre} config {numero}: PR-AUC={pr_auc:.4f}, "
                f"F2={f2_val:.4f}, t={threshold:.4f}, {segundos:.1f}s"
            )

        if mejor is None:
            raise AssertionError(f"No se evaluaron configuraciones para {nombre}.")
        final = _estimador(nombre, mejor["parametros"])
        inicio = time.perf_counter()
        final.fit(X_train, y_train)
        segundos_final = time.perf_counter() - inicio
        prob_test = final.predict_proba(X_test)[:, 1]
        m05, _ = metricas_binarias(y_test, prob_test, 0.5)
        mop, _ = metricas_binarias(y_test, prob_test, mejor["umbral"])
        m05.update({"modelo": nombre, "tipo_umbral": "0.5", "segundos_ajuste_final": segundos_final})
        mop.update({"modelo": nombre, "tipo_umbral": "operativo_F2", "segundos_ajuste_final": segundos_final})
        metricas_05.append(m05)
        metricas_operativas.append(mop)
        slug = nombre.lower().replace(" ", "_").replace("ó", "o")
        joblib.dump(final, modelos_dir / f"{slug}.joblib", compress=3)
        predicciones[f"prob_{slug}"] = prob_test.astype("float32")
        umbrales[nombre] = float(mejor["umbral"])
        parametros_elegidos[nombre] = mejor["parametros"]
        print(
            f"{nombre} final: PR-AUC={mop['pr_auc']:.4f}, recall={mop['recall']:.4f}, "
            f"precision={mop['precision']:.4f}, F2={mop['f2']:.4f}"
        )

    df_busqueda = pd.DataFrame(filas_busqueda)
    df_05 = pd.DataFrame(metricas_05)
    df_operativas = pd.DataFrame(metricas_operativas)
    df_busqueda.to_csv(rutas["busqueda"], index=False)
    df_05.to_csv(rutas["metricas_05"], index=False)
    df_operativas.to_csv(rutas["metricas_operativas"], index=False)
    predicciones.to_parquet(rutas["predicciones"], index=False, compression="zstd")

    prevalencia_muestra = float(datos[OBJETIVO].mean())
    manifest = {
        "modeling_version": MODELING_VERSION,
        "random_state": RANDOM_STATE,
        "muestra_total": int(len(datos)),
        "train_n": int(len(train)),
        "test_n": int(len(test)),
        "test_size": TEST_SIZE,
        "prevalencia_muestra": prevalencia_muestra,
        "positivos_train": int(y_train.sum()),
        "positivos_test": int(y_test.sum()),
        "test_sha256": _hash_test(test),
        "predictores": PREDICTORAS,
        "criterio_hiperparametros": "Máximo PR-AUC; desempate por F2 en validación interna",
        "criterio_umbral": "Máximo F2 en validación interna (recall pesa cuatro veces precision)",
        "parametros_elegidos": parametros_elegidos,
        "umbrales_operativos": umbrales,
    }
    rutas["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Puertas de calidad.
    assert len(train) == 420_000 and len(test) == 180_000
    assert abs(train[OBJETIVO].mean() - test[OBJETIVO].mean()) < 1e-4
    assert VARIABLES_PROHIBIDAS.isdisjoint(PREDICTORAS)
    assert df_05["modelo"].nunique() == df_operativas["modelo"].nunique() == 3
    assert np.isfinite(df_operativas[["accuracy", "precision", "recall", "f1", "roc_auc"]]).all().all()

    return {"salida": salida, **rutas, "manifest_data": manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--reuse", action="store_true")
    args = parser.parse_args()
    resultado = ejecutar_modelos(args.project_dir, args.output_dir, reutilizar=args.reuse)
    print(json.dumps(resultado["manifest_data"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
