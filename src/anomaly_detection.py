from __future__ import annotations

import pandas as pd

from .config import ANOMALY_DIRECTIONS, KPI_COLUMNS


def detect_anomalies(
    kpi_df: pd.DataFrame,
    window: int = 24,
    z_threshold: float = 2.2,
) -> pd.DataFrame:
    """Flag per-cell KPI anomalies with rolling z-score baselines."""
    df = kpi_df.sort_values(["cell_id", "timestamp"]).copy()
    anomaly_cols: list[str] = []

    for kpi in KPI_COLUMNS:
        rolling = df.groupby("cell_id")[kpi].transform(
            lambda s: s.rolling(window=window, min_periods=8).mean()
        )
        rolling_std = df.groupby("cell_id")[kpi].transform(
            lambda s: s.rolling(window=window, min_periods=8).std()
        )
        z_col = f"{kpi}_z"
        flag_col = f"{kpi}_anomaly"
        df[z_col] = ((df[kpi] - rolling) / rolling_std.replace(0, pd.NA)).fillna(0)

        if ANOMALY_DIRECTIONS[kpi] == "high":
            df[flag_col] = df[z_col] > z_threshold
        else:
            df[flag_col] = df[z_col] < -z_threshold
        anomaly_cols.append(flag_col)

    df["anomaly_count"] = df[anomaly_cols].sum(axis=1)
    df["has_anomaly"] = df["anomaly_count"] > 0
    return df


def get_cell_context(
    anomaly_df: pd.DataFrame,
    cell_id: str,
    alarm_time: pd.Timestamp,
    hours_before: int = 12,
    hours_after: int = 2,
) -> pd.DataFrame:
    start = alarm_time - pd.Timedelta(hours=hours_before)
    end = alarm_time + pd.Timedelta(hours=hours_after)
    return anomaly_df[
        (anomaly_df["cell_id"] == cell_id)
        & (anomaly_df["timestamp"] >= start)
        & (anomaly_df["timestamp"] <= end)
    ].copy()


def summarize_anomaly_evidence(context_df: pd.DataFrame, required_kpis: list[str]) -> list[dict]:
    evidence: list[dict] = []
    if context_df.empty:
        return evidence

    for kpi in required_kpis:
        flag_col = f"{kpi}_anomaly"
        z_col = f"{kpi}_z"
        if flag_col not in context_df:
            continue
        hits = context_df[context_df[flag_col]].sort_values(z_col, key=lambda s: s.abs(), ascending=False)
        if hits.empty:
            latest = context_df.sort_values("timestamp").iloc[-1]
            evidence.append(
                {
                    "kpi": kpi,
                    "status": "no_anomaly_in_window",
                    "timestamp": str(latest["timestamp"]),
                    "value": round(float(latest[kpi]), 3),
                    "z_score": round(float(latest[z_col]), 3),
                }
            )
            continue
        top = hits.iloc[0]
        evidence.append(
            {
                "kpi": kpi,
                "status": "anomaly",
                "timestamp": str(top["timestamp"]),
                "value": round(float(top[kpi]), 3),
                "z_score": round(float(top[z_col]), 3),
            }
        )
    return evidence
