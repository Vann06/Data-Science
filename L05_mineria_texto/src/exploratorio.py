"""Funciones reutilizables para el analisis exploratorio de tweets de desastres."""

import re
from pathlib import Path

import pandas as pd

try:
    from nltk.corpus import stopwords as nltk_stopwords
except ImportError:  # pragma: no cover
    nltk_stopwords = None

# Palabras propias del lenguaje de Twitter que no aportan significado
# y que no vienen incluidas en las stopwords estandar de nltk.
EXTRA_STOPWORDS = {
    "rt", "amp", "im", "u", "via", "like", "get", "one", "new",
}

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_SYMBOL_RE = re.compile(r"#")
HTML_ENTITY_RE = re.compile(r"&\w+;")
NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
MULTISPACE_RE = re.compile(r"\s+")


def load_data(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Carga train, test y sample_submission desde data/raw."""
    data_dir = Path(data_dir)
    return {
        "train": pd.read_csv(data_dir / "train.csv"),
        "test": pd.read_csv(data_dir / "test.csv"),
        "sample_submission": pd.read_csv(data_dir / "sample_submission.csv"),
    }


def get_stopwords() -> set[str]:
    """Stopwords en ingles (nltk) + ruido propio de tweets."""
    base = set(nltk_stopwords.words("english")) if nltk_stopwords else set()
    return base | EXTRA_STOPWORDS


def clean_text(text: str) -> str:
    """Limpieza basica de un tweet: minusculas, sin URLs/menciones/HTML/puntuacion."""
    text = str(text).lower()
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = HTML_ENTITY_RE.sub(" ", text)
    text = HASHTAG_SYMBOL_RE.sub(" ", text)  # se conserva la palabra, se quita el simbolo
    text = NON_ALPHA_RE.sub(" ", text)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


def tokenize_clean(text: str, stopwords: set[str] | None = None) -> list[str]:
    """Limpia y tokeniza un tweet, removiendo stopwords y palabras muy cortas."""
    stopwords = stopwords if stopwords is not None else get_stopwords()
    cleaned = clean_text(text)
    return [
        word for word in cleaned.split()
        if word not in stopwords and len(word) > 2
    ]
