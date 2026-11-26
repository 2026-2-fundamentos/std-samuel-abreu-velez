"""
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """

import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]


def pregunta_09():
    conteo = {}
    for fila in leer_registros():
        for par in fila[4].split(","):
            clave = par.split(":")[0]
            conteo[clave] = conteo.get(clave, 0) + 1
    return dict(sorted(conteo.items()))

def main():
    print(pregunta_09())


if __name__ == "__main__":
    main()