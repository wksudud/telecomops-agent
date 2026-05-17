from __future__ import annotations

from pathlib import Path
import random

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
KB_DIR = ROOT / "knowledge_base"


def inject_incident(df: pd.DataFrame, cell_id: str, start_idx: int, alarm_type: str) -> None:
    mask = (df["cell_id"] == cell_id) & (df.groupby("cell_id").cumcount().between(start_idx, start_idx + 5))
    if alarm_type == "HIGH_DROP_RATE":
        df.loc[mask, "drop_rate"] += 2.8
        df.loc[mask, "handover_success_rate"] -= 7.5
    elif alarm_type == "LOW_THROUGHPUT":
        df.loc[mask, "throughput_mbps"] -= 35
        df.loc[mask, "latency_ms"] += 45
    elif alarm_type == "CELL_UNAVAILABLE":
        df.loc[mask, "availability"] -= 18
        df.loc[mask, "attach_success_rate"] -= 14
    elif alarm_type == "HIGH_LATENCY":
        df.loc[mask, "latency_ms"] += 65
        df.loc[mask, "throughput_mbps"] -= 18


def main() -> None:
    random.seed(7)
    np.random.seed(7)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)

    cells = [f"CELL-{idx:03d}" for idx in range(1, 11)]
    timestamps = pd.date_range("2026-05-01 00:00:00", periods=24 * 7, freq="h")
    rows = []
    for cell in cells:
        region = random.choice(["north", "east", "west"])
        load_factor = random.uniform(0.85, 1.2)
        for ts in timestamps:
            hour_shape = 1 + 0.25 * np.sin((ts.hour - 8) / 24 * 2 * np.pi)
            rows.append(
                {
                    "timestamp": ts,
                    "cell_id": cell,
                    "region": region,
                    "drop_rate": max(0.2, np.random.normal(0.9 * load_factor, 0.16)),
                    "handover_success_rate": min(99.5, np.random.normal(96.5, 0.7)),
                    "throughput_mbps": max(8, np.random.normal(88 / load_factor * hour_shape, 9)),
                    "latency_ms": max(12, np.random.normal(31 * load_factor, 5)),
                    "availability": min(99.99, np.random.normal(99.55, 0.12)),
                    "attach_success_rate": min(99.6, np.random.normal(97.8, 0.5)),
                }
            )
    kpi = pd.DataFrame(rows)

    incidents = [
        ("ALARM-1001", "CELL-003", 92, "HIGH_DROP_RATE", "major", "Drop rate increased after handover failures."),
        ("ALARM-1002", "CELL-007", 104, "LOW_THROUGHPUT", "major", "User throughput sharply degraded during busy hours."),
        ("ALARM-1003", "CELL-005", 118, "CELL_UNAVAILABLE", "critical", "Cell unavailable and attach success dropped."),
        ("ALARM-1004", "CELL-002", 130, "HIGH_LATENCY", "minor", "Latency spike observed with throughput degradation."),
    ]
    for _, cell_id, start_idx, alarm_type, _, _ in incidents:
        inject_incident(kpi, cell_id, start_idx, alarm_type)

    alarms = []
    for alarm_id, cell_id, start_idx, alarm_type, severity, description in incidents:
        alarms.append(
            {
                "alarm_id": alarm_id,
                "timestamp": timestamps[start_idx + 4],
                "cell_id": cell_id,
                "severity": severity,
                "alarm_type": alarm_type,
                "description": description,
                "status": "open",
            }
        )
    alarms_df = pd.DataFrame(alarms)
    tickets_df = pd.DataFrame(
        [
            {
                "ticket_id": "TICKET-HIST-001",
                "alarm_id": "ALARM-HIST-001",
                "priority": "P2",
                "assignee": "noc-engineer-a",
                "status": "resolved",
                "summary": "Historical low throughput case for demo comparison.",
            }
        ]
    )

    kpi.to_csv(DATA_DIR / "kpi.csv", index=False)
    alarms_df.to_csv(DATA_DIR / "alarms.csv", index=False)
    tickets_df.to_csv(DATA_DIR / "tickets.csv", index=False)

    (KB_DIR / "radio_fault_manual.md").write_text(
        """# Radio Fault Manual

## HIGH_DROP_RATE
Symptoms include sudden drop rate increase, reduced handover success rate, and user complaints around mobility. Likely causes include radio interference, neighbor relation mismatch, antenna degradation, or recent parameter changes. Recommended checks: compare neighboring cells, inspect handover relation changes, review RF alarms, and schedule drive-test if remote checks are inconclusive.

## CELL_UNAVAILABLE
Symptoms include availability drop, attach failures, and site heartbeat loss. Likely causes include power outage, RRU/BBU hardware fault, transmission interruption, or maintenance window misconfiguration. Recommended checks: site power, transmission link, board status, and remote reset result.
""",
        encoding="utf-8",
    )
    (KB_DIR / "transport_fault_manual.md").write_text(
        """# Transport Fault Manual

## LOW_THROUGHPUT
Throughput degradation with latency increase often indicates transport congestion, packet loss, or capacity bottleneck. Check backhaul utilization, packet errors, route changes, and PRB utilization before dispatching capacity expansion work.

## HIGH_LATENCY
Latency spikes can come from transport delay, core path congestion, or routing changes. Compare neighboring cells and inspect packet loss, jitter, route updates, and user-plane gateway metrics.
""",
        encoding="utf-8",
    )
    print(f"generated kpi_rows={len(kpi)} alarms={len(alarms_df)} data_dir={DATA_DIR}")


if __name__ == "__main__":
    main()
