"""
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """
import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]


def pregunta_10():
    return [
        (fila[0], len(fila[3].split(",")), len(fila[4].split(",")))
        for fila in leer_registros()
    ]
    
def main():
    print(pregunta_10())


if __name__ == "__main__":
    main()