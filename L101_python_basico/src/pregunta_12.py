
"""
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]


def pregunta_12():
    sumas = {}
    for fila in leer_registros():
        total = sum(int(par.split(":")[1]) for par in fila[4].split(","))
        sumas[fila[0]] = sumas.get(fila[0], 0) + total
    return dict(sorted(sumas.items()))

def main():
    print(pregunta_12())


if __name__ == "__main__":
    main()
