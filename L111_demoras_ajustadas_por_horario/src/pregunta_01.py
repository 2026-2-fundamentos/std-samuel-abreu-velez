from pathlib import Path

import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "flights_by_carrier_day_hour.csv.gz"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"

MIN_FLIGHTS = 100_000


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Construye `hourly_delay_rates.csv` y `carrier_adjusted_delays.csv` en
    `submission/` y retorna las dos tablas, en ese orden.
    """
    df = pd.read_csv(INPUT_FILE)

    # 1. Tasa nacional de demora por hora programada de salida (todas las aerolíneas).
    hourly = (
        df.groupby("scheduled_departure_hour")[
            ["operated_flights", "delayed_departure_15_flights"]
        ]
        .sum()
        .reset_index()
    )
    hourly["delay_rate"] = (
        hourly["delayed_departure_15_flights"] / hourly["operated_flights"]
    )

    # 2. Demoras esperadas por aerolínea: vuelos de cada hora x tasa nacional de esa hora.
    por_hora = (
        df.groupby(["reporting_airline", "scheduled_departure_hour"])[
            ["operated_flights", "delayed_departure_15_flights"]
        ]
        .sum()
        .reset_index()
        .merge(
            hourly[["scheduled_departure_hour", "delay_rate"]],
            on="scheduled_departure_hour",
        )
    )
    por_hora["expected_delayed_flights"] = (
        por_hora["operated_flights"] * por_hora["delay_rate"]
    )

    carriers = (
        por_hora.groupby("reporting_airline")[
            ["operated_flights", "delayed_departure_15_flights", "expected_delayed_flights"]
        ]
        .sum()
        .reset_index()
    )
    carriers = carriers[carriers["operated_flights"] >= MIN_FLIGHTS].copy()

    # 3. Razón observadas / esperadas y rankings (1 = peor aerolínea).
    carriers["delay_rate"] = (
        carriers["delayed_departure_15_flights"] / carriers["operated_flights"]
    )
    carriers["observed_to_expected_ratio"] = (
        carriers["delayed_departure_15_flights"] / carriers["expected_delayed_flights"]
    )
    carriers["crude_rank"] = (
        carriers["delay_rate"].rank(ascending=False, method="min").astype(int)
    )
    carriers["adjusted_rank"] = (
        carriers["observed_to_expected_ratio"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    carriers = carriers.sort_values("adjusted_rank").reset_index(drop=True)

    carriers = carriers[
        [
            "reporting_airline",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
            "expected_delayed_flights",
            "observed_to_expected_ratio",
            "crude_rank",
            "adjusted_rank",
        ]
    ]

    # Presentación: conteos enteros y valores decimales redondeados.
    for tabla in (hourly, carriers):
        tabla["operated_flights"] = tabla["operated_flights"].astype(int)
        tabla["delayed_departure_15_flights"] = tabla[
            "delayed_departure_15_flights"
        ].astype(int)
        tabla["delay_rate"] = tabla["delay_rate"].round(6)
    carriers["expected_delayed_flights"] = carriers["expected_delayed_flights"].round(4)
    carriers["observed_to_expected_ratio"] = carriers[
        "observed_to_expected_ratio"
    ].round(6)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(SUBMISSION_DIR / "hourly_delay_rates.csv", index=False)
    carriers.to_csv(SUBMISSION_DIR / "carrier_adjusted_delays.csv", index=False)

    return hourly, carriers


if __name__ == "__main__":
    pregunta_01()
