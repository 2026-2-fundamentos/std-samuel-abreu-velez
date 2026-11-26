from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sin ventana: solo guarda el archivo

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "sales.csv.gz"
SUBMISSION_DIR = PROJECT_FOLDER / "submission"


def numero_de_mes(periodo):
    """Convierte un Period mensual en un entero (año * 12 + mes)."""
    return periodo.dt.year * 12 + periodo.dt.month


def dibujar_mapa_de_calor(retencion, ultimo_mes, ruta):
    # Matriz cohorte x período. Dentro del rango observable, una cohorte sin
    # clientes activos en un período tiene retención 0; más allá del último mes
    # de los datos el período aún no existe y queda vacío (NaN).
    matriz = retencion.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    periodos = list(range(int(retencion["period_index"].max()) + 1))
    matriz = matriz.reindex(columns=periodos)

    for cohorte in matriz.index:
        inicio = pd.Period(cohorte, freq="M")
        maximo = (ultimo_mes - inicio).n
        for periodo in periodos:
            if periodo <= maximo and pd.isna(matriz.loc[cohorte, periodo]):
                matriz.loc[cohorte, periodo] = 0.0

    valores = np.ma.masked_invalid(matriz.to_numpy())
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("white")

    fig, ax = plt.subplots(figsize=(1.1 * len(periodos) + 2, 0.6 * len(matriz) + 2))
    imagen = ax.imshow(valores, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(periodos)))
    ax.set_xticklabels(periodos)
    ax.set_yticks(range(len(matriz)))
    ax.set_yticklabels(matriz.index)
    ax.set_xlabel("Período (meses desde la primera compra)")
    ax.set_ylabel("Cohorte (mes de la primera compra)")
    ax.set_title("Retención de clientes por cohorte")

    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            valor = matriz.iat[i, j]
            if not np.isnan(valor):
                color = "white" if valor > 0.6 else "black"
                ax.text(j, i, f"{valor:.0%}", ha="center", va="center", color=color)

    barra = fig.colorbar(imagen, ax=ax)
    barra.set_label("Tasa de retención")
    barra.ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")

    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def build_cohort_analysis() -> pd.DataFrame:
    """
    Calcula la retención por cohorte de `data/sales.csv.gz`, guarda
    `submission/cohort_retention.csv` y `submission/cohort_retention_heatmap.png`
    y retorna la tabla de retención.
    """
    df = pd.read_csv(INPUT_FILE, usecols=["CustomerID", "OrderDate"])
    df["order_month"] = pd.to_datetime(df["OrderDate"]).dt.to_period("M")
    df["cohort_period"] = df.groupby("CustomerID")["order_month"].transform("min")
    df["period_index"] = numero_de_mes(df["order_month"]) - numero_de_mes(
        df["cohort_period"]
    )
    df["cohort_month"] = df["cohort_period"].astype(str)

    retencion = (
        df.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    tamano = (
        retencion[retencion["period_index"] == 0]
        .set_index("cohort_month")["active_customers"]
        .rename("cohort_size")
    )
    retencion = retencion.merge(tamano, on="cohort_month")
    retencion["retention_rate"] = (
        retencion["active_customers"] / retencion["cohort_size"]
    ).round(6)
    retencion = retencion.sort_values(["cohort_month", "period_index"]).reset_index(
        drop=True
    )

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    retencion.to_csv(SUBMISSION_DIR / "cohort_retention.csv", index=False)
    dibujar_mapa_de_calor(
        retencion,
        df["order_month"].max(),
        SUBMISSION_DIR / "cohort_retention_heatmap.png",
    )

    return retencion


if __name__ == "__main__":
    build_cohort_analysis()
