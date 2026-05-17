from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"

KPI_COLUMNS = [
    "drop_rate",
    "handover_success_rate",
    "throughput_mbps",
    "latency_ms",
    "availability",
    "attach_success_rate",
]

ANOMALY_DIRECTIONS = {
    "drop_rate": "high",
    "handover_success_rate": "low",
    "throughput_mbps": "low",
    "latency_ms": "high",
    "availability": "low",
    "attach_success_rate": "low",
}

DEFAULT_RULES = {
    "HIGH_DROP_RATE": {
        "root_cause": "radio interference or coverage degradation",
        "required_kpis": ["drop_rate", "handover_success_rate"],
        "actions": [
            "Check recent radio parameter changes.",
            "Inspect neighboring cell interference and handover relations.",
            "Prioritize drive-test or remote RF optimization for the affected cell.",
        ],
    },
    "LOW_THROUGHPUT": {
        "root_cause": "capacity congestion or transport bottleneck",
        "required_kpis": ["throughput_mbps", "latency_ms"],
        "actions": [
            "Check PRB utilization and active user count.",
            "Inspect transport link errors and backhaul congestion.",
            "Schedule capacity expansion if congestion is persistent.",
        ],
    },
    "CELL_UNAVAILABLE": {
        "root_cause": "base station hardware, power, or transmission failure",
        "required_kpis": ["availability", "attach_success_rate"],
        "actions": [
            "Verify site power and RRU/BBU alarms.",
            "Check transmission status and site heartbeat.",
            "Dispatch field engineer if remote recovery fails.",
        ],
    },
    "HIGH_LATENCY": {
        "root_cause": "core network path congestion or transport delay",
        "required_kpis": ["latency_ms", "throughput_mbps"],
        "actions": [
            "Compare latency across neighboring cells.",
            "Inspect transport route and packet loss.",
            "Escalate to core/transport team if multi-cell symptoms appear.",
        ],
    },
}
