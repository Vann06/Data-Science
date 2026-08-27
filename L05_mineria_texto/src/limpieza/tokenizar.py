#tokenizar por palabras
"""Tokenizacion de los tweets ya limpios.

Se usa TweetTokenizer de nltk, disenado para texto de redes sociales.
Como en este punto del pipeline el texto ya viene sin URLs, sin puntuacion y
sin simbolos, el tokenizador se limita a separar palabras, pero se mantiene
por ser el estandar para este tipo de corpus.

Este modulo SOLO separa: el filtrado por longitud se hace en el paso de
stopwords, que es el que conoce la lista de negaciones a preservar (de otro
modo un filtro de longitud aqui borraria 'no', que mide 2 caracteres).
"""

from nltk.tokenize import TweetTokenizer

_TOKENIZER = TweetTokenizer(preserve_case=False, reduce_len=False, strip_handles=False)


def tokenizar(texto: str) -> list[str]:
    """Separa el texto limpio en una lista de tokens."""
    return _TOKENIZER.tokenize(str(texto))
