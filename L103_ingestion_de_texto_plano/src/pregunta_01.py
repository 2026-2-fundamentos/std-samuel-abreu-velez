import re
from pathlib import Path

import pandas as pd

INPUT_FILE = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"

# Primera línea de un clúster: número, cantidad, porcentaje con coma y "%",
# y el inicio de la lista de palabras clave.
FILA = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+(?:,\d+)?)\s*%\s*(.*)$")


def unir_partes(partes):
    """Une las líneas de un clúster. Si una línea termina en guion, la palabra
    compuesta continúa en la siguiente línea y se pega sin espacio."""
    texto = ""
    for parte in partes:
        parte = " ".join(parte.split())
        if not parte:
            continue
        if texto.endswith("-"):
            texto += parte
        elif texto:
            texto += " " + parte
        else:
            texto = parte
    return texto


def pregunta_01():
    """
    Convierte `data/clusters_report.txt` en un DataFrame con una fila por
    clúster y las columnas `cluster`, `cantidad_de_palabras_clave`,
    `porcentaje_de_palabras_clave` y `principales_palabras_clave`.
    """
    registros = []

    with open(INPUT_FILE, encoding="utf-8") as archivo:
        for linea in archivo:
            coincidencia = FILA.match(linea)

            if coincidencia:
                cluster, cantidad, porcentaje, texto = coincidencia.groups()
                registros.append(
                    {
                        "cluster": int(cluster),
                        "cantidad_de_palabras_clave": int(cantidad),
                        "porcentaje_de_palabras_clave": float(
                            porcentaje.replace(",", ".")
                        ),
                        "partes": [texto],
                    }
                )
            elif registros and linea.strip():
                # Línea de continuación de las palabras clave del último clúster.
                registros[-1]["partes"].append(linea)

    for registro in registros:
        texto = unir_partes(registro.pop("partes"))
        registro["principales_palabras_clave"] = texto.rstrip(".").strip()

    return pd.DataFrame(
        registros,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )


if __name__ == "__main__":
    print(pregunta_01())
