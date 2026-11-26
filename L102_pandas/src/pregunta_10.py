from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_10():
    """
    Valores de `c2` por categoría de `c1`, ordenados y unidos con `:`.
    """

    df = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    resultado = df.groupby("c1")["c2"].apply(
        lambda s: ":".join(str(v) for v in sorted(s))
    )
    return resultado.sort_index().to_frame()


if __name__ == "__main__":
    print(pregunta_10())
