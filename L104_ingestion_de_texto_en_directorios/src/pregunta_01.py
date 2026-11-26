from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_FOLDER / "data"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"


def construir_dataset(split):
    """Recorre data/<split>/<sentimiento>/*.txt en orden alfabético."""
    frases = []
    targets = []

    for carpeta in sorted(p for p in (DATA_DIR / split).iterdir() if p.is_dir()):
        for archivo in sorted(carpeta.glob("*.txt")):
            with open(archivo, encoding="utf-8") as f:
                frases.append(f.read().strip())
            targets.append(carpeta.name)

    return pd.DataFrame({"phrase": frases, "target": targets})


def pregunta_01():
    """
    Construye `submission/train_dataset.csv` y `submission/test_dataset.csv`
    a partir de los archivos `.txt` de `data/train/` y `data/test/`, con las
    columnas `phrase` y `target` y sin índice.
    """
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    for split in ("train", "test"):
        df = construir_dataset(split)
        df.to_csv(SUBMISSION_DIR / f"{split}_dataset.csv", index=False)


if __name__ == "__main__":
    pregunta_01()
