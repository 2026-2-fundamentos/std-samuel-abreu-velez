from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_11():
    """
    Una fila por `c0` con las letras de `c4` ordenadas y separadas por comas.
    """

    df = pd.read_csv(DATA_DIR / "tbl1.tsv", sep="\t")
    resultado = (
        df.groupby("c0")["c4"]
        .apply(lambda s: ",".join(sorted(s)))
        .reset_index()
        .sort_values("c0")
        .reset_index(drop=True)
    )
    return resultado


if __name__ == "__main__":
    print(pregunta_11())
