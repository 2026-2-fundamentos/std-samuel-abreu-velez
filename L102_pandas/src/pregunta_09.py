from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_09():
    """
    Tabla tbl0 con columna `year` (texto de 4 caracteres) tomada de c3.
    """

    df = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    df["year"] = df["c3"].astype(str).str[:4]
    return df


if __name__ == "__main__":
    print(pregunta_09())
