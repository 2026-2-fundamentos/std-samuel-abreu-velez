
"""
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]

def pregunta_11():
    sumas = {}
    for fila in leer_registros():
        for letra in fila[3].split(","):
            sumas[letra] = sumas.get(letra, 0) + int(fila[1])
    return dict(sorted(sumas.items()))

def main():
    print(pregunta_11())


if __name__ == "__main__":
    main()
    raise NotImplementedError
