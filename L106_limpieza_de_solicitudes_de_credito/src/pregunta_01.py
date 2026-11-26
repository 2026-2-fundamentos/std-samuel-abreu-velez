import csv
import gzip
import re
from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "solicitudes_de_credito.csv.gz"
OUTPUT_FILE = PROJECT_FOLDER / "submission" / "solicitudes_de_credito.csv"

COLUMNAS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]
COLUMNAS_TEXTO = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]
FALTANTES = {"", "nan", "na", "n/a", "none", "null"}


def normalizar_encabezado(nombre):
    nombre = str(nombre).replace("\ufeff", "").strip().lower().replace(" ", "_")
    return "línea_credito" if nombre == "linea_credito" else nombre


def leer_datos():
    with gzip.open(INPUT_FILE, "rt", encoding="utf-8-sig", newline="") as f:
        muestra = f.read(4096)
        f.seek(0)
        try:
            sep = csv.Sniffer().sniff(muestra, delimiters=",;\t|").delimiter
        except csv.Error:
            sep = ";"
        df = pd.read_csv(f, sep=sep, dtype=str, keep_default_na=False)
    df.columns = [normalizar_encabezado(c) for c in df.columns]
    # Se descarta la columna de índice y cualquier otra que no pertenezca a los datos.
    return df[COLUMNAS].copy()


def limpiar_texto(valor):
    valor = re.sub(r"[_\-]+", " ", valor.lower())
    return " ".join(valor.split())


def limpiar_estrato(valor):
    coincidencia = re.search(r"\d+", valor)
    return int(coincidencia.group()) if coincidencia else None


def limpiar_monto(valor):
    valor = re.sub(r"[^\d.,]", "", valor)
    valor = re.sub(r"[.,]\d{1,2}$", "", valor)  # centavos, p. ej. ".00"
    valor = re.sub(r"[.,]", "", valor)  # separadores de miles
    return int(valor) if valor else None


def limpiar_fecha(valor):
    valor = valor.strip().split(" ")[0].replace("/", "-")
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", valor):
        año, mes, dia = valor.split("-")
    elif re.fullmatch(r"\d{1,2}-\d{1,2}-\d{4}", valor):
        dia, mes, año = valor.split("-")
    else:
        return None
    try:
        return pd.Timestamp(int(año), int(mes), int(dia)).strftime("%Y-%m-%d")
    except ValueError:
        return None


def pregunta_01():
    """
    Limpia `data/solicitudes_de_credito.csv.gz` y lo guarda en
    `submission/solicitudes_de_credito.csv` con separador `;` y sin índice.
    """
    df = leer_datos()

    # Texto: minúsculas, guiones y guiones bajos como espacios, sin espacios extra.
    for col in COLUMNAS_TEXTO:
        df[col] = df[col].map(limpiar_texto)

    df["estrato"] = df["estrato"].map(limpiar_estrato)
    df["monto_del_credito"] = df["monto_del_credito"].map(limpiar_monto)
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].map(limpiar_fecha)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].str.strip()

    # Registros incompletos: todas las columnas salvo comuna_ciudadano.
    obligatorias = [c for c in COLUMNAS if c != "comuna_ciudadano"]
    for col in obligatorias:
        if col in COLUMNAS_TEXTO:
            df.loc[df[col].str.lower().isin(FALTANTES), col] = None
    df = df.dropna(subset=obligatorias)

    df["estrato"] = df["estrato"].astype(int)
    df["monto_del_credito"] = df["monto_del_credito"].astype(int)

    df = df.drop_duplicates().reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")


if __name__ == "__main__":
    pregunta_01()
