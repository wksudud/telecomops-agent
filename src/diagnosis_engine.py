from __future__ import annotations

import pandas as pd

from .anomaly_detection import summarize_anomaly_evidence
from .config import DEFAULT_RULES
from .schemas import DiagnosisResult, KnowledgeHit


def diagnose_alarm(
    alarm: dict,
    kpi_context: pd.DataFrame,
    knowledge_hits: list[KnowledgeHit],
    rules: dict = DEFAULT_RULES,
) -> DiagnosisResult:
    alarm_type = str(alarm["alarm_type"])
    rule = rules.get(
        alarm_type,
        {
            "root_cause": "unknown network degradation",
            "required_kpis": [],
            "actions": ["Collect more KPI and alarm evidence before dispatch."],
        },
    )
    evidence = summarize_anomaly_evidence(kpi_context, rule["required_kpis"])
    anomaly_hits = sum(1 for item in evidence if item["status"] == "anomaly")
    kpi_score = anomaly_hits / max(len(rule["required_kpis"]), 1)
    knowledge_score = min(sum(hit.score for hit in knowledge_hits[:2]), 1.0)
    severity_score = {"critical": 0.2, "major": 0.14, "minor": 0.08}.get(str(alarm["severity"]), 0.05)
    confidence = min(0.45 + 0.35 * kpi_score + 0.15 * knowledge_score + severity_score, 0.98)

    assumptions = []
    if not evidence:
        assumptions.append("No KPI evidence was available in the diagnosis window.")
    if not knowledge_hits:
        assumptions.append("No matching fault manual snippet was retrieved.")
    assumptions.append("All demo data is synthetic and should not be treated as real operator telemetry.")

    return DiagnosisResult(
        alarm_id=str(alarm["alarm_id"]),
        cell_id=str(alarm["cell_id"]),
        alarm_type=alarm_type,
        severity=str(alarm["severity"]),
        root_cause=rule["root_cause"],
        confidence=round(confidence, 3),
        kpi_evidence=evidence,
        knowledge_hits=knowledge_hits,
        recommended_actions=list(rule["actions"]),
        assumptions=assumptions,
    )
