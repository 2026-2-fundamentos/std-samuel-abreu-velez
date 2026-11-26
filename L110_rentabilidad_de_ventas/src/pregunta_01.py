from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "superstore_orders.csv.gz"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"

BANDS = ["0%", "1%-5%", "6%-10%", "más de 10%"]
EPS = 1e-9  # tolerancia para comparar proporciones decimales


def asignar_rango(descuento):
    return np.select(
        [
            descuento <= EPS,
            descuento <= 0.05 + EPS,
            descuento <= 0.10 + EPS,
        ],
        BANDS[:3],
        default=BANDS[3],
    )


def resumir(df, claves):
    """Medidas de rentabilidad por grupo, sin usar groupby.apply."""
    es_perdida = df["Profit"] < 0
    tabla = df.assign(
        _perdida=es_perdida.astype(int),
        _utilidad_perdida=(-df["Profit"]).where(es_perdida, 0.0),
    )
    resumen = tabla.groupby(claves).agg(
        lines=("Profit", "size"),
        orders=("Order ID", "nunique"),
        sales=("Sales", "sum"),
        profit=("Profit", "sum"),
        loss_lines=("_perdida", "sum"),
        lost_profit=("_utilidad_perdida", "sum"),
    )
    resumen["profit_margin"] = resumen["profit"] / resumen["sales"]
    resumen["loss_line_rate"] = resumen["loss_lines"] / resumen["lines"]
    return resumen.reset_index()


def redondear(tabla):
    tabla = tabla.copy()
    tabla["sales"] = tabla["sales"].round(2)
    for col in ("profit", "lost_profit"):
        tabla[col] = tabla[col].round(4)
    for col in ("profit_margin", "loss_line_rate"):
        if col in tabla.columns:
            tabla[col] = tabla[col].round(4)
    return tabla


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Genera `profitability_summary.csv`, `discount_summary.csv` y
    `priority_segments.csv` en `submission/` y retorna las tres tablas.
    """
    df = pd.read_csv(INPUT_FILE, sep=";", decimal=",", encoding="utf-8-sig")
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]

    # 1. Resumen general (una sola fila).
    profitability = resumir(df.assign(_todo=1), "_todo")
    profitability = redondear(
        profitability[
            [
                "lines",
                "orders",
                "sales",
                "profit",
                "profit_margin",
                "loss_lines",
                "loss_line_rate",
                "lost_profit",
            ]
        ]
    )

    # 2. Resumen por rango de descuento, en el orden definido.
    df["discount_band"] = asignar_rango(df["Discount"].to_numpy())
    discount = resumir(df, "discount_band")
    discount["_orden"] = discount["discount_band"].map(BANDS.index)
    discount = discount.sort_values("_orden")
    discount = redondear(
        discount[
            [
                "discount_band",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "loss_line_rate",
                "lost_profit",
            ]
        ]
    ).reset_index(drop=True)

    # 3. Cinco segmentos segmento-categoría con mayor utilidad perdida.
    claves = ["Customer Segment", "Product Category"]
    segmentos = resumir(df, claves)
    segmentos = segmentos[segmentos["lines"] >= 100]
    segmentos = segmentos.sort_values("lost_profit", ascending=False, kind="stable")
    priority = redondear(
        segmentos.head(5)[
            claves + ["lines", "sales", "profit", "profit_margin", "lost_profit"]
        ]
    ).reset_index(drop=True)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    profitability.to_csv(SUBMISSION_DIR / "profitability_summary.csv", index=False)
    discount.to_csv(SUBMISSION_DIR / "discount_summary.csv", index=False)
    priority.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return profitability, discount, priority


if __name__ == "__main__":
    pregunta_01()
