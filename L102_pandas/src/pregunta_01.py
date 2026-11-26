from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_01():
    """
    Cantidad de registros de `data/tbl0.tsv`.
    """

    df = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    return len(df)


if __name__ == "__main__":
    print(pregunta_01())
