from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_FOLDER / "data"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"

CANALES = {"letter": "historical_requests_letter.csv.gz", "web": "historical_requests_web.csv.gz"}
DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PLAZO = 15  # días hábiles


def cargar_canal(canal, archivo):
    """Lee un canal y elimina las filas idénticas. Las filas sin record_id se conservan."""
    df = pd.read_csv(DATA_DIR / archivo).drop_duplicates()
    df["channel"] = canal
    return df


def agregar_tiempos(df):
    entrada = pd.to_datetime(df["in_date"])
    salida = pd.to_datetime(df["out_date"])
    respondida = salida.notna()

    df["year"] = entrada.dt.year
    df["answered"] = respondida
    df["calendar_days"] = (salida - entrada).dt.days

    # Días hábiles (lunes a viernes) posteriores a la entrada, hasta la salida incluida:
    # el intervalo [entrada + 1 día, salida + 1 día).
    inicio = (entrada + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    fin = (salida + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    habiles = np.full(len(df), np.nan)
    habiles[respondida.to_numpy()] = np.busday_count(
        inicio[respondida.to_numpy()], fin[respondida.to_numpy()]
    )
    df["business_days"] = habiles

    # Una solicitud pendiente no ha cumplido el plazo (NaN <= 15 es False).
    df["on_time"] = df["business_days"] <= PLAZO
    return df


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Genera `channel_summary.csv`, `yearly_summary.csv` y `entry_day_summary.csv`
    en `submission/` y retorna las tres tablas, en ese orden.
    """
    df = pd.concat(
        [cargar_canal(canal, archivo) for canal, archivo in CANALES.items()],
        ignore_index=True,
    )
    df = agregar_tiempos(df)

    # 1. Resumen por canal (orden alfabético: letter, web).
    channel = (
        df.groupby("channel")
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            median_business_days=("business_days", "median"),
            on_time=("on_time", "sum"),
        )
        .reset_index()
    )
    channel["pending"] = channel["requests"] - channel["answered"]
    channel["on_time_rate"] = (channel["on_time"] / channel["requests"]).round(6)
    channel = channel[
        ["channel", "requests", "answered", "pending", "median_business_days", "on_time_rate"]
    ]

    # 2. Resumen por año de entrada y canal.
    yearly = (
        df.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            on_time=("on_time", "sum"),
        )
        .reset_index()
    )
    yearly["pending"] = yearly["requests"] - yearly["answered"]
    yearly["on_time_rate"] = (yearly["on_time"] / yearly["requests"]).round(6)
    yearly = yearly.sort_values(["year", "channel"])[
        ["year", "channel", "requests", "pending", "on_time_rate"]
    ].reset_index(drop=True)

    # 3. Resumen por día de entrada (lunes a domingo, canales juntos).
    entry_day = (
        df.groupby("day_name")
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reindex(DIAS)
        .reset_index()
    )

    for tabla in (channel, yearly, entry_day):
        tabla["requests"] = tabla["requests"].astype(int)
    channel["answered"] = channel["answered"].astype(int)
    channel["pending"] = channel["pending"].astype(int)
    yearly["pending"] = yearly["pending"].astype(int)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    channel.to_csv(SUBMISSION_DIR / "channel_summary.csv", index=False)
    yearly.to_csv(SUBMISSION_DIR / "yearly_summary.csv", index=False)
    entry_day.to_csv(SUBMISSION_DIR / "entry_day_summary.csv", index=False)

    return channel, yearly, entry_day


if __name__ == "__main__":
    pregunta_01()
