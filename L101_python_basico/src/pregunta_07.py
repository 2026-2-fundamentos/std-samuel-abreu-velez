import csv
import gzip
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def leer_registros():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as f:
        return [fila for fila in csv.reader(f, delimiter="\t") if fila]


def pregunta_07():
    grupos = {}
    for fila in leer_registros():
        grupos.setdefault(int(fila[1]), []).append(fila[0])
    return sorted(grupos.items())

def main():
    print(pregunta_07())


if __name__ == "__main__":
    main()