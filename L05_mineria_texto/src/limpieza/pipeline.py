"""Orquestador del pipeline de limpieza.

Orden de los pasos y por que ese orden:

1. normalizacion  -> minusculas + contracciones. Va PRIMERO porque expandir
                     "don't" necesita el apostrofe, que el paso 2 elimina.
2. limpieza_ruido -> links (con flag), menciones/hashtags sin simbolo pero con
                     su flag adjunto ('#fire' -> 'flaghashtag fire'), y emojis.
                     La puntuacion se pospone para que el paso 3 lea los
                     numeros completos ('13,000').
3. marcar_numeros -> cambia los numeros por flags, distinguiendo el 911.
                     Va DESPUES de quitar los links para no marcar los digitos
                     que venian dentro de una URL.
4. tokenizar      -> separa en tokens.
5. stopwords      -> quita palabras vacias y tokens cortos, preservando negaciones.
6. lem / stem     -> reduce cada token a su forma base.
7. n_gramas       -> combina unigramas..n_max para conservar contexto.
"""

from pathlib import Path

import pandas as pd

from .eliminacion_palabras_vacias import (
    construir_corpus_stopwords,
    eliminar_palabras_vacias,
)
from .lem import lematizar
from .limpieza_ruido import limpiar_ruido_previo, quitar_puntuacion
from .n_gramas import generar_hasta_n
from .normalizacion import marcar_numeros, normalizar
from .stem import aplicar_stemming
from .tokenizar import tokenizar


def procesar_texto(
    texto: str,
    corpus_stopwords: set[str],
    n_ngramas: int = 2,
    metodo_raiz: str = "lema",
) -> dict:
    """Aplica el pipeline completo a un tweet y devuelve cada etapa intermedia."""
    normalizado = normalizar(texto)
    # Se limpia el ruido SIN tocar la puntuacion todavia: marcar los numeros
    # necesita '13,000' entero, y necesita que las URLs ya no esten.
    sin_ruido, flags_ruido = limpiar_ruido_previo(normalizado)
    con_flags, flag_emergencia = marcar_numeros(sin_ruido)
    sin_puntuacion = quitar_puntuacion(con_flags)
    tokens = tokenizar(sin_puntuacion)
    sin_stopwords = eliminar_palabras_vacias(tokens, corpus_stopwords)

    if metodo_raiz == "lema":
        raices = lematizar(sin_stopwords)
    elif metodo_raiz == "stem":
        raices = aplicar_stemming(sin_stopwords)
    else:
        raise ValueError("metodo_raiz debe ser 'lema' o 'stem'")

    ngramas = generar_hasta_n(raices, n_ngramas)

    return {
        "texto_normalizado": normalizado,
        "texto_sin_ruido": sin_ruido,
        "texto_con_flags": sin_puntuacion,
        **flags_ruido,  # tiene_link, tiene_mencion, tiene_hashtag
        "menciona_911": flag_emergencia,
        "tokens": tokens,
        "tokens_sin_stopwords": sin_stopwords,
        "tokens_procesados": raices,
        "ngramas": ngramas,
        "texto_limpio": " ".join(raices),
        "texto_ngramas": " ".join(ngramas),
    }


def procesar_dataframe(
    df: pd.DataFrame,
    columna_texto: str = "text",
    n_ngramas: int = 2,
    metodo_raiz: str = "lema",
) -> pd.DataFrame:
    """Aplica el pipeline a toda una columna de texto, agregando las etapas como columnas."""
    corpus = construir_corpus_stopwords()
    resultados = df[columna_texto].apply(
        lambda t: procesar_texto(t, corpus, n_ngramas=n_ngramas, metodo_raiz=metodo_raiz)
    )
    etapas = pd.DataFrame(list(resultados), index=df.index)
    return pd.concat([df, etapas], axis=1)


def nombre_archivo_salida(nombre_base: str, n_ngramas: int, metodo_raiz: str = "lema") -> str:
    """Construye el nombre del CSV procesado dejando el n de los n-gramas explicito."""
    return f"{nombre_base}_limpio_{metodo_raiz}_{n_ngramas}gramas.csv"


def guardar_procesado(
    df: pd.DataFrame,
    directorio: str | Path,
    nombre_base: str,
    n_ngramas: int,
    metodo_raiz: str = "lema",
) -> Path:
    """Guarda el dataframe procesado en data/processed con el n en el nombre."""
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / nombre_archivo_salida(nombre_base, n_ngramas, metodo_raiz)

    # Las columnas de listas se serializan como texto separado por espacios
    # para que el CSV sea legible y facil de recargar.
    df_salida = df.copy()
    for col in ["tokens", "tokens_sin_stopwords", "tokens_procesados", "ngramas"]:
        if col in df_salida.columns:
            df_salida[col] = df_salida[col].apply(" ".join)

    df_salida.to_csv(ruta, index=False)
    return ruta
