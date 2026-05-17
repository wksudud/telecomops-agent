from __future__ import annotations

import pandas as pd
import plotly.express as px

from .config import KPI_COLUMNS


def kpi_line_chart(kpi_df: pd.DataFrame, cell_id: str, kpi: str = "drop_rate"):
    cell_df = kpi_df[kpi_df["cell_id"] == cell_id]
    return px.line(cell_df, x="timestamp", y=kpi, title=f"{cell_id} {kpi}")


def alarm_severity_chart(alarms_df: pd.DataFrame):
    counts = alarms_df["severity"].value_counts().reset_index()
    counts.columns = ["severity", "count"]
    return px.bar(counts, x="severity", y="count", title="Alarm severity distribution")


def anomaly_heatmap(anomaly_df: pd.DataFrame):
    pivot = anomaly_df.pivot_table(
        index="cell_id",
        columns=anomaly_df["timestamp"].dt.hour,
        values="anomaly_count",
        aggfunc="sum",
        fill_value=0,
    )
    return px.imshow(pivot, title="Anomaly count by cell and hour", aspect="auto")


def available_kpis() -> list[str]:
    return KPI_COLUMNS
