"""Descarga las bases originales y diccionarios desde el INE, sin sobrescribir."""
import json
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent

def descargar(item):
    nombre, url = item
    destino = ROOT / nombre
    if destino.exists():
        return f"Existe: {nombre}"
    try:
        with urlopen(url, timeout=120) as respuesta:
            contenido = respuesta.read()
        if not contenido.startswith(b"PK"):
            raise ValueError("La respuesta no es un archivo XLSX")
        destino.write_bytes(contenido)
        return f"Descargado: {nombre} ({len(contenido):,} bytes)"
    except Exception as error:
        return f"ERROR {nombre}: {error}"

if __name__ == "__main__":
    fuentes = json.loads((ROOT / "fuentes.json").read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=5) as pool:
        for mensaje in pool.map(descargar, fuentes.items()):
            print(mensaje, flush=True)
    if any(not (ROOT / nombre).exists() for nombre in fuentes):
        raise SystemExit(1)
