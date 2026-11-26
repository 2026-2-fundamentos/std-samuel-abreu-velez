from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_13():
    """
    Une tbl0 y tbl2 por `c0` y suma `c5b` por categoría de `c1`.
    """

    tbl0 = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    tbl2 = pd.read_csv(DATA_DIR / "tbl2.tsv", sep="\t")
    unido = tbl0.merge(tbl2, on="c0")
    return unido.groupby("c1")["c5b"].sum().sort_index()


if __name__ == "__main__":
    print(pregunta_13())
