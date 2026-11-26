import csv
import gzip
import json
import re
from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "ventas.csv.gz"
OUTPUT_FILE = PROJECT_FOLDER / "submission" / "data_quality_report.json"

REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]

EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s.]+\.[^@\s]+")


def normalizar_columna(nombre):
    return nombre.replace("\ufeff", "").strip().lower().replace(" ", "_")


def leer_datos():
    """Lee el archivo sin modificar valores: todo como texto, sin NaN."""
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8-sig", newline="") as f:
        muestra = f.read(4096)
        f.seek(0)
        try:
            delimitador = csv.Sniffer().sniff(muestra, delimiters=",;\t|").delimiter
        except csv.Error:
            delimitador = ","
        df = pd.read_csv(
            f, sep=delimitador, dtype=str, keep_default_na=False, na_filter=False
        )
    df.columns = [normalizar_columna(c) for c in df.columns]
    return df


def es_faltante(serie):
    limpia = serie.str.strip()
    return (limpia == "") | (limpia == "N/A")


def main():
    """
    Genera `submission/data_quality_report.json` con el diagnóstico de calidad
    de `data/ventas.csv.gz` (sin limpiar los datos) y retorna el reporte.
    """
    df = leer_datos()
    columnas = list(df.columns)

    reporte = {
        "row_count": int(len(df)),
        "column_count": int(len(columnas)),
        "missing_required_columns": sorted(set(REQUIRED_COLUMNS) - set(columnas)),
        "unexpected_columns": sorted(set(columnas) - set(REQUIRED_COLUMNS)),
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": (
            int(df.duplicated(subset="supplier_id", keep=False).sum())
            if "supplier_id" in df.columns
            else 0
        ),
        "missing_value_count_by_column": {
            col: int(es_faltante(df[col]).sum()) for col in columnas
        },
    }

    if "contact_email" in df.columns:
        reporte["invalid_email_count"] = int(
            sum(EMAIL_PATTERN.fullmatch(v) is None for v in df["contact_email"])
        )
    else:
        reporte["invalid_email_count"] = 0

    if "units" in df.columns:
        presentes = df.loc[~es_faltante(df["units"]), "units"]
        numeros = pd.to_numeric(presentes, errors="coerce").dropna()
        invalidos = (numeros <= 0) | (numeros != numeros.round())
        reporte["invalid_unit_count"] = int(invalidos.sum())
    else:
        reporte["invalid_unit_count"] = 0

    reporte["country_values"] = (
        sorted(set(df["country"])) if "country" in df.columns else []
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return reporte


if __name__ == "__main__":
    main()
