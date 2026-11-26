from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_08():
    """
    Tabla tbl0 con columna `suma` = c0 + c2.
    """

    df = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    df["suma"] = df["c0"] + df["c2"]
    return df


if __name__ == "__main__":
    print(pregunta_08())
