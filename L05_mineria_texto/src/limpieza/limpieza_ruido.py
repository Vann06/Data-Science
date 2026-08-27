"""Limpieza de ruido propio de Twitter.

Criterios (definidos para este laboratorio):
- Menciones y hashtags SE CONSERVAN como palabra, pero se les quita el simbolo
  (@ / #). La palabra del hashtag suele ser justamente el termino del desastre,
  asi que tirarla perderia senal.
- Ademas se les ADJUNTA un flag delante que recuerda de donde venia la palabra:
  '#earthquake' -> 'flaghashtag earthquake'
  '@bbcmtd'     -> 'flagmencion bbcmtd'
  El flag va DELANTE para que el bigrama resultante sea legible y capture la
  relacion completa ('flaghashtag_earthquake' = "el hashtag earthquake"),
  mientras el unigrama 'earthquake' sigue existiendo por separado y sumando
  a la misma feature que cuando la palabra aparece sin '#'. Si se sustituyera
  la palabra por algo como 'hashtagearthquake' se perderia esa union.
- Los links se eliminan, PERO se sustituyen por un espacio para no pegar la
  palabra que venia despues, y se levanta un flag indicando que el tweet
  traia un link (el EDA mostro que la presencia de URL discrimina: 66% de los
  tweets de desastre real la tienen vs 41% de los que no).
- Se quitan emojis y signos de puntuacion.
"""

import re

URL_RE = re.compile(r"https?://\S+|www\.\S+")
# Se acepta el '@' pegado a otro caracter porque en el corpus 58 menciones
# legitimas vienen precedidas de puntuacion ('.@NorwayMFA', "'@Alexis_Sanchez").
# El costo es marcar como mencion el '@' de las groserias censuradas
# ('f$&@ing'), que ocurre en 1 solo tweet de 7613.
MENCION_RE = re.compile(r"@(\w+)")
HASHTAG_RE = re.compile(r"#(\w+)")
HTML_ENTITY_RE = re.compile(r"&(?:amp|lt|gt|quot|#\d+);")
# Rangos unicode de emojis y pictogramas.
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # simbolos y pictogramas
    "\U0001F600-\U0001F64F"  # emoticones
    "\U0001F680-\U0001F6FF"  # transporte y mapas
    "\U0001F700-\U0001F77F"
    "\U0001F900-\U0001F9FF"  # suplemento de pictogramas
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000027BF"  # simbolos varios y dingbats
    "\U0000FE00-\U0000FE0F"  # selectores de variacion
    "\U00002700-\U000027BF"
    "]+",
    flags=re.UNICODE,
)
# Flags que se adjuntan a la palabra de la mencion / del hashtag. Son una sola
# palabra (sin '_' ni digitos) para sobrevivir a la limpieza de puntuacion, al
# filtro de longitud minima y para no chocar con el separador de n-gramas.
FLAG_HASHTAG = "flaghashtag"
FLAG_MENCION = "flagmencion"

PUNTUACION_RE = re.compile(r"[^\w\s]")
SOLO_NUMEROS_RE = re.compile(r"\b\d+\b")
GUION_BAJO_RE = re.compile(r"_+")
MULTISPACE_RE = re.compile(r"\s+")


def tiene_link(texto: str) -> bool:
    """Indica si el tweet contenia al menos un link (flag para el modelo)."""
    return bool(URL_RE.search(str(texto)))


def quitar_links(texto: str) -> str:
    """Elimina URLs reemplazandolas por espacio (no pega las palabras vecinas)."""
    return URL_RE.sub(" ", texto)


def tiene_mencion(texto: str) -> bool:
    """Indica si el tweet traia al menos una mencion (@usuario)."""
    return bool(MENCION_RE.search(str(texto)))


def tiene_hashtag(texto: str) -> bool:
    """Indica si el tweet traia al menos un hashtag (#palabra)."""
    return bool(HASHTAG_RE.search(str(texto)))


def desmarcar_menciones_hashtags(texto: str, adjuntar_flag: bool = True) -> str:
    """Conserva la palabra de menciones y hashtags, quitando '@' y '#'.

    Con adjuntar_flag=True (por defecto) antepone el flag correspondiente, de
    modo que se conserve la palabra Y el hecho de que venia marcada.
    """
    if adjuntar_flag:
        texto = MENCION_RE.sub(rf"{FLAG_MENCION} \1", texto)
        texto = HASHTAG_RE.sub(rf"{FLAG_HASHTAG} \1", texto)
    else:
        texto = MENCION_RE.sub(r"\1", texto)
        texto = HASHTAG_RE.sub(r"\1", texto)
    return texto


def quitar_emojis(texto: str) -> str:
    """Elimina emojis y pictogramas unicode."""
    return EMOJI_RE.sub(" ", texto)


def quitar_puntuacion(texto: str, conservar_numeros: bool = False) -> str:
    """Quita signos de puntuacion; opcionalmente tambien los numeros sueltos."""
    texto = PUNTUACION_RE.sub(" ", texto)
    texto = GUION_BAJO_RE.sub(" ", texto)  # \w incluye '_', que aqui es ruido
    if not conservar_numeros:
        texto = SOLO_NUMEROS_RE.sub(" ", texto)
    return texto


def limpiar_ruido_previo(
    texto: str, adjuntar_flag: bool = True
) -> tuple[str, dict[str, bool]]:
    """Quita links, entidades HTML, simbolos de menciones/hashtags y emojis.

    NO toca la puntuacion, a proposito: el pipeline necesita marcar los
    numeros antes de que se elimine, porque quitar la coma de '13,000' lo
    partiria en dos numeros ('13' y '000') y generaria flags duplicados.

    Devuelve (texto, flags), donde flags trae 'tiene_link', 'tiene_mencion' y
    'tiene_hashtag' para guardarlos como columnas del dataframe.
    """
    texto = str(texto)
    flag_link = tiene_link(texto)

    texto = quitar_links(texto)
    texto = HTML_ENTITY_RE.sub(" ", texto)

    # Se detectan menciones y hashtags DESPUES de quitar los links, porque una
    # URL puede traer un '#fragmento' que no es un hashtag del tweet.
    flags = {
        "tiene_link": flag_link,
        "tiene_mencion": tiene_mencion(texto),
        "tiene_hashtag": tiene_hashtag(texto),
    }

    texto = desmarcar_menciones_hashtags(texto, adjuntar_flag=adjuntar_flag)
    texto = quitar_emojis(texto)
    texto = MULTISPACE_RE.sub(" ", texto).strip()

    return texto, flags


def limpiar_ruido(
    texto: str, conservar_numeros: bool = False, adjuntar_flag: bool = True
) -> tuple[str, dict[str, bool]]:
    """Limpieza de ruido completa, en un solo paso (incluyendo puntuacion).

    Version standalone del modulo. El pipeline no la usa: intercala el marcado
    de numeros entre limpiar_ruido_previo() y quitar_puntuacion().
    """
    texto, flags = limpiar_ruido_previo(texto, adjuntar_flag=adjuntar_flag)
    texto = quitar_puntuacion(texto, conservar_numeros=conservar_numeros)
    texto = MULTISPACE_RE.sub(" ", texto).strip()

    return texto, flags
