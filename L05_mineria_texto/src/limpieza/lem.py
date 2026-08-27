##hacer lemematizacion con las palabras
"""Lematizacion con WordNet.

La lematizacion reduce cada palabra a su forma de diccionario respetando el
idioma ('fires' -> 'fire', 'burning' -> 'burn'), a diferencia del stemming que
corta de forma mecanica. Para elegir bien el lema hace falta la categoria
gramatical, asi que se etiqueta con el POS tagger de NLTK.

Es el metodo por defecto del pipeline: conserva palabras reales, lo que
importa para poder leer los n-gramas y la nube de palabras.
"""

from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

_LEMATIZADOR = WordNetLemmatizer()

# Mapeo de las etiquetas del Penn Treebank a las que entiende WordNet.
_MAPA_POS = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}


def _pos_wordnet(etiqueta_treebank: str) -> str:
    """Traduce una etiqueta POS de Treebank a WordNet (sustantivo por defecto)."""
    return _MAPA_POS.get(etiqueta_treebank[0].upper(), wordnet.NOUN)


def lematizar(tokens: list[str]) -> list[str]:
    """Lematiza una lista de tokens usando su categoria gramatical."""
    if not tokens:
        return []
    return [
        _LEMATIZADOR.lemmatize(token, _pos_wordnet(etiqueta))
        for token, etiqueta in pos_tag(tokens)
    ]
