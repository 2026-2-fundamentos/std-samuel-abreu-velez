import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "insurance.csv.gz"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"
REPORT_FILE = SUBMISSION_DIR / "privacy_report.json"
PUBLISHED_FILE = SUBMISSION_DIR / "insurance_published.csv"

K = 5
ORIGINAL_QI = ["age", "sex", "bmi", "children", "region"]
SCHEMES = {
    "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
    "without_children": ["age_group", "sex", "bmi_group", "region"],
}


def agregar_grupos(df):
    df = df.copy()
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 29, 39, 49, 64],
        labels=["18-29", "30-39", "40-49", "50-64"],
    ).astype(str)
    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[-np.inf, 18.5, 25, 30, np.inf],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,
    ).astype(str)
    df["children_group"] = np.where(
        df["children"] == 0, "0", np.where(df["children"] <= 2, "1-2", "3+")
    )
    return df


def evaluar_esquema(df, columnas):
    tamano = df.groupby(columnas)["smoker"].transform("size")
    publicado = df[tamano >= K]

    clases = df.groupby(columnas).size()
    clases_pub = publicado.groupby(columnas)["smoker"].agg(
        n="size", distintos="nunique"
    )
    sin_diversidad = clases_pub[clases_pub["distintos"] == 1]

    resumen = {
        "quasi_identifiers": columnas,
        "equivalence_classes": int(len(clases)),
        "k_before_suppression": int(clases.min()),
        "suppressed_records": int((tamano < K).sum()),
        "published_records": int(len(publicado)),
        "published_classes": int(len(clases_pub)),
        "classes_without_smoker_diversity": int(len(sin_diversidad)),
        "records_without_smoker_diversity": int(sin_diversidad["n"].sum()),
    }
    return resumen, publicado


def pregunta_01():
    """
    Mide el riesgo de reidentificación de `data/insurance.csv.gz`, elige el
    esquema de generalización que suprime menos registros y escribe
    `submission/privacy_report.json` e `submission/insurance_published.csv`.
    """
    df = pd.read_csv(INPUT_FILE)
    df = agregar_grupos(df)

    tamanos_originales = df.groupby(ORIGINAL_QI)["age"].transform("size")
    original_k = int(df.groupby(ORIGINAL_QI).size().min())
    unicos = int((tamanos_originales == 1).sum())

    esquemas = {}
    publicados = {}
    for nombre, columnas in SCHEMES.items():
        esquemas[nombre], publicados[nombre] = evaluar_esquema(df, columnas)

    seleccionado = min(esquemas, key=lambda n: esquemas[n]["suppressed_records"])
    publicado = publicados[seleccionado]

    reporte = {
        "original_k": original_k,
        "original_unique_records": unicos,
        "schemes": esquemas,
        "selected_scheme": seleccionado,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(publicado["charges"].mean()),
        "smoker_rate_original": float((df["smoker"] == "yes").mean()),
        "smoker_rate_published": float((publicado["smoker"] == "yes").mean()),
    }

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    columnas_salida = SCHEMES[seleccionado] + ["smoker", "charges"]
    publicado[columnas_salida].to_csv(PUBLISHED_FILE, index=False)

    return reporte


if __name__ == "__main__":
    pregunta_01()