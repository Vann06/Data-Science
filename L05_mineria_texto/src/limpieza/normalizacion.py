#llevar las palabras a lower, talvez podriamos guardar los numeors, para tener en cuenta el 911
#si el numero es 911 dejar el flag de numero y de emergencia, si es un numero que no es 911 dejar el flag de numero y de no emergencia
"""Normalizacion del texto: minusculas, contracciones, alargamientos y numeros.

El modulo expone DOS funciones que se ejecutan en momentos distintos del
pipeline, porque dependen de cosas opuestas:

- normalizar()     -> va PRIMERO (paso 1). Expandir "don't" -> "do not"
                      necesita el apostrofe, que la limpieza de ruido elimina
                      junto al resto de la puntuacion.
- marcar_numeros() -> va DESPUES de quitar los links (paso 2.5). Si se
                      ejecutara antes, los digitos que vienen dentro de las
                      URLs ('t.co/lHYXEOHY6C', '13000') se marcarian como
                      numeros del tweet, que es justo lo que no queremos.

Sobre los numeros: en vez de borrarlos se reemplazan por flags, distinguiendo
el 911 (numero de emergencias en EE.UU., donde ocurre la mayoria de los tweets
del dataset) del resto. Asi el modelo recibe "aqui habia un numero y era una
llamada de emergencia" sin tener que aprender un vocabulario de miles de
cifras distintas, que solo agregarian ruido.
"""

import re
import unicodedata

# Contracciones del ingles. Las negativas van primero porque son las que
# interesa preservar para el analisis (don't -> do not).
CONTRACCIONES = {
    "ain't": "is not", "aren't": "are not", "can't": "cannot",
    "couldn't": "could not", "didn't": "did not", "doesn't": "does not",
    "don't": "do not", "hadn't": "had not", "hasn't": "has not",
    "haven't": "have not", "isn't": "is not", "mightn't": "might not",
    "mustn't": "must not", "needn't": "need not", "shan't": "shall not",
    "shouldn't": "should not", "wasn't": "was not", "weren't": "were not",
    "won't": "will not", "wouldn't": "would not",
    "i'm": "i am", "i've": "i have", "i'll": "i will", "i'd": "i would",
    "you're": "you are", "you've": "you have", "you'll": "you will",
    "you'd": "you would", "he's": "he is", "he'll": "he will",
    "he'd": "he would", "she's": "she is", "she'll": "she will",
    "she'd": "she would", "it's": "it is", "it'll": "it will",
    "it'd": "it would", "we're": "we are", "we've": "we have",
    "we'll": "we will", "we'd": "we would", "they're": "they are",
    "they've": "they have", "they'll": "they will", "they'd": "they would",
    "that's": "that is", "that'll": "that will", "there's": "there is",
    "there'll": "there will", "what's": "what is", "what're": "what are",
    "who's": "who is", "where's": "where is", "let's": "let us",
    "y'all": "you all", "'cause": "because",
}

# Numeros que corresponden a una llamada de emergencia.
NUMEROS_EMERGENCIA = {"911"}

# Flags que sustituyen a los numeros. Son una sola palabra (sin '_' ni
# digitos) para sobrevivir a la limpieza de puntuacion, al filtro de longitud
# minima y para no confundirse con el separador de n-gramas.
FLAG_NUMERO = "flagnumero"
FLAG_EMERGENCIA = "flagemergencia"
FLAG_NO_EMERGENCIA = "flagnoemergencia"

# Apostrofes tipograficos que Twitter suele traer.
APOSTROFES_RE = re.compile(r"[‘’ʼ´`]")
# 3+ letras repetidas -> 2 (soooo -> soo), conserva el enfasis sin explotar el
# vocabulario. Se limita a letras para no alterar numeros como '13,000'.
ALARGAMIENTO_RE = re.compile(r"([a-z])\1{2,}")
# Numeros posiblemente con separadores de miles o decimales (13,000 / 3.5).
NUMERO_RE = re.compile(r"\b\d[\d.,]*\b")
MULTISPACE_RE = re.compile(r"\s+")


def normalizar_unicode(texto: str) -> str:
    """Descompone acentos y elimina los artefactos de mojibake tipicos del dataset.

    Los tweets traen secuencias como '\\x89Û_' por una mala decodificacion en
    el origen; no aportan informacion y se descartan junto al resto de
    caracteres no ASCII.
    """
    texto = unicodedata.normalize("NFKD", texto)
    return texto.encode("ascii", "ignore").decode("ascii")


def expandir_contracciones(texto: str) -> str:
    """Expande contracciones del ingles para preservar las negaciones."""
    texto = APOSTROFES_RE.sub("'", texto)
    for contraccion, expansion in CONTRACCIONES.items():
        texto = re.sub(rf"\b{re.escape(contraccion)}\b", expansion, texto)
    # Contracciones negativas no listadas explicitamente (p. ej. formas raras).
    texto = re.sub(r"\b(\w+)n't\b", r"\1 not", texto)
    return texto


def reducir_alargamientos(texto: str) -> str:
    """Reduce letras repetidas 3+ veces a 2 (helppp -> helpp)."""
    return ALARGAMIENTO_RE.sub(r"\1\1", texto)


def es_numero_emergencia(numero: str) -> bool:
    """Indica si el numero encontrado es un numero de emergencia (911)."""
    return numero.strip(".,") in NUMEROS_EMERGENCIA


def _reemplazar_numero(match: re.Match) -> str:
    """Sustituye un numero por su par de flags (numero + tipo)."""
    if es_numero_emergencia(match.group()):
        return f" {FLAG_NUMERO} {FLAG_EMERGENCIA} "
    return f" {FLAG_NUMERO} {FLAG_NO_EMERGENCIA} "


def marcar_numeros(texto: str) -> tuple[str, bool]:
    """Reemplaza los numeros por flags y avisa si el tweet mencionaba el 911.

    Debe ejecutarse DESPUES de quitar los links, para no marcar los digitos
    que forman parte de una URL.

    Devuelve (texto_con_flags, menciona_emergencia).
    """
    texto = str(texto)
    menciona_emergencia = any(
        es_numero_emergencia(m.group()) for m in NUMERO_RE.finditer(texto)
    )
    texto = NUMERO_RE.sub(_reemplazar_numero, texto)
    return MULTISPACE_RE.sub(" ", texto).strip(), menciona_emergencia


def normalizar(texto: str) -> str:
    """Pipeline de normalizacion: minusculas + unicode + contracciones + alargamientos.

    Los numeros NO se tocan aqui: se marcan con marcar_numeros() una vez que
    los links ya fueron eliminados.
    """
    texto = str(texto).lower()
    texto = normalizar_unicode(texto)
    texto = expandir_contracciones(texto)
    texto = reducir_alargamientos(texto)
    return MULTISPACE_RE.sub(" ", texto).strip()
