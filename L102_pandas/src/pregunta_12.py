from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_12():
    """
    Una fila por `c0` con los textos `c5a:c5b` ordenados y unidos por comas.
    """

    df = pd.read_csv(DATA_DIR / "tbl2.tsv", sep="\t")
    df["c5"] = df["c5a"] + ":" + df["c5b"].astype(str)
    resultado = (
        df.groupby("c0")["c5"]
        .apply(lambda s: ",".join(sorted(s)))
        .reset_index()
        .sort_values("c0")
        .reset_index(drop=True)
    )
    return resultado


if __name__ == "__main__":
    print(pregunta_12())
