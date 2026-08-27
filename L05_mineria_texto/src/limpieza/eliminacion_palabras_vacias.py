"""Eliminacion de palabras vacias (stopwords), conservando las negaciones.

El corpus base es el de stopwords en ingles de NLTK (179 palabras), al que se
le suma ruido propio de Twitter ('rt', 'amp', ...) detectado en el EDA.

De ese corpus se RESTAN las negaciones: NLTK considera stopwords a 'no',
'not', 'nor', etc., pero en clasificacion de desastres invierten el sentido
de la frase ('no fire' vs 'fire'), asi que se conservan.
"""

from nltk.corpus import stopwords as nltk_stopwords

# Negaciones y modificadores que NLTK marca como stopwords pero que aqui
# se conservan porque cambian el significado del tweet.
NEGACIONES = {
    "no", "not", "nor", "none", "never", "neither", "nothing", "nobody",
    "nowhere", "cannot", "cant", "without", "against", "don", "aren",
    "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "mightn",
    "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn",
    "ain",
}

# Ruido propio del lenguaje de Twitter, sin carga semantica.
STOPWORDS_TWITTER = {
    "rt", "amp", "via", "im", "lol", "gt", "lt", "http", "https", "co",
}

# Longitud minima de un token para conservarlo (las negaciones quedan exentas).
MIN_LONGITUD = 3


def construir_corpus_stopwords(
    incluir_twitter: bool = True,
    conservar_negaciones: bool = True,
) -> set[str]:
    """Arma el conjunto final de stopwords a eliminar."""
    corpus = set(nltk_stopwords.words("english"))
    if incluir_twitter:
        corpus |= STOPWORDS_TWITTER
    if conservar_negaciones:
        corpus -= NEGACIONES
    return corpus


def eliminar_palabras_vacias(
    tokens: list[str],
    corpus: set[str] | None = None,
    min_longitud: int = MIN_LONGITUD,
) -> list[str]:
    """Quita stopwords y tokens demasiado cortos, preservando las negaciones."""
    corpus = corpus if corpus is not None else construir_corpus_stopwords()
    return [
        token for token in tokens
        if token in NEGACIONES or (token not in corpus and len(token) >= min_longitud)
    ]
