from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_07():
    """
    Suma de `c2` por categoría de `c1`.
    """

    df = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    return df.groupby("c1")["c2"].sum().sort_index()


if __name__ == "__main__":
    print(pregunta_07())
