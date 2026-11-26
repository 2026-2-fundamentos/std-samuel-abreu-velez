
"""
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
""" 
import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]


def pregunta_08():
    grupos = {}
    for fila in leer_registros():
        grupos.setdefault(int(fila[1]), set()).add(fila[0])
    return [(valor, sorted(letras)) for valor, letras in sorted(grupos.items())]

def main():
    print(pregunta_08())


if __name__ == "__main__":
    main()