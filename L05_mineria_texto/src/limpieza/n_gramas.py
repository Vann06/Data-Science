#construit los ngramas, dejar la variable de cuantos n gramas queremos para poder agregarlo como parametro
"""Generacion de n-gramas.

Un n-grama es una secuencia de n tokens consecutivos. Los unigramas pierden
el contexto: en el EDA se vio que 'fire', 'body' o 'emergency' aparecen en
ambas clases, mientras que bigramas como 'forest_fire' o 'body_bag'
desambiguan el sentido. Por eso el pipeline combina unigramas + bigramas.

El tamano n es un parametro (`n_ngramas` en el pipeline), de modo que se
pueda cambiar a 3 y regenerar los datos sin tocar el codigo.

Los tokens de un n-grama se unen con '_' para que cada n-grama funcione como
un unico termino al vectorizar.
"""

SEPARADOR = "_"


def generar_ngramas(tokens: list[str], n: int) -> list[str]:
    """Devuelve los n-gramas de tamano exactamente n."""
    if n < 1:
        raise ValueError("n debe ser >= 1")
    if len(tokens) < n:
        return []
    return [SEPARADOR.join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def generar_hasta_n(tokens: list[str], n_max: int) -> list[str]:
    """Combina todos los n-gramas desde 1 hasta n_max.

    Con n_max=2 devuelve unigramas + bigramas, que es la configuracion por
    defecto del pipeline.
    """
    ngramas: list[str] = []
    for n in range(1, n_max + 1):
        ngramas.extend(generar_ngramas(tokens, n))
    return ngramas
