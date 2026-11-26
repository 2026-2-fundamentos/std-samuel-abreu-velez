from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_PATTERN = "bank-marketing-campaing-*.csv.gz"
OUTPUT_DIR = PROJECT_FOLDER / "submission"

MESES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}  # fmt: skip


def leer_archivos():
    """Lee directamente los .csv.gz (pandas descomprime por la extensión)."""
    archivos = sorted((PROJECT_FOLDER / "data").glob(INPUT_PATTERN))
    tablas = [pd.read_csv(archivo) for archivo in archivos]
    df = pd.concat(tablas, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]
    return df


def a_binario(serie, valor):
    return (serie == valor).astype(int)


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Separa los archivos `data/bank-marketing-campaing-*.csv.gz` en las tablas
    `client`, `campaign` y `economics`, las guarda en `submission/` y las
    retorna en ese orden.
    """
    df = leer_archivos()

    # --- client ---
    client = df[
        ["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]
    ].copy()
    client["job"] = client["job"].str.replace(".", "", regex=False).str.replace(
        "-", "_", regex=False
    )
    client["education"] = client["education"].str.replace(".", "_", regex=False)
    client["education"] = client["education"].mask(client["education"] == "unknown")
    client["credit_default"] = a_binario(client["credit_default"], "yes")
    client["mortgage"] = a_binario(client["mortgage"], "yes")

    # --- campaign ---
    campaign = df[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
        ]
    ].copy()
    campaign["previous_outcome"] = a_binario(campaign["previous_outcome"], "success")
    campaign["campaign_outcome"] = a_binario(campaign["campaign_outcome"], "yes")
    mes = df["month"].astype(str).str.strip().str.lower().str[:3].map(MESES)
    fecha = pd.to_datetime({"year": 2022, "month": mes, "day": df["day"]})
    campaign["last_contact_date"] = fecha.dt.strftime("%Y-%m-%d")

    # --- economics ---
    economics = df[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client.to_csv(OUTPUT_DIR / "client.csv", index=False)
    campaign.to_csv(OUTPUT_DIR / "campaign.csv", index=False)
    economics.to_csv(OUTPUT_DIR / "economics.csv", index=False)

    return client, campaign, economics


if __name__ == "__main__":
    clean_campaign_data()
