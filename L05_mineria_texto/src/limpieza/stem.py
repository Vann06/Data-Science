## hacer steaming con las palabras
"""Stemming con el algoritmo de Porter.

Corta los sufijos de forma mecanica ('burning' -> 'burn', pero tambien
'families' -> 'famili'), por lo que produce raices que no siempre son
palabras reales. Reduce mas el vocabulario que la lematizacion.

Se deja disponible como alternativa a lem.py: el pipeline acepta
metodo_raiz='stem' para comparar el efecto de ambas estrategias sobre el
tamano del vocabulario.
"""

from nltk.stem import PorterStemmer

_STEMMER = PorterStemmer()


def aplicar_stemming(tokens: list[str]) -> list[str]:
    """Reduce cada token a su raiz de Porter."""
    return [_STEMMER.stem(token) for token in tokens]
