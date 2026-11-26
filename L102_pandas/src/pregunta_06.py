from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_06():
    """
    Valores distintos de `c4` (tbl1) en mayúsculas, ordenados.
    """

    df = pd.read_csv(DATA_DIR / "tbl1.tsv", sep="\t")
    return sorted(df["c4"].str.upper().unique().tolist())


if __name__ == "__main__":
    print(pregunta_06())
