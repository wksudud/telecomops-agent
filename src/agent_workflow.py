from __future__ import annotations

import json
from pathlib import Path

from .anomaly_detection import detect_anomalies, get_cell_context
from .data_loader import load_alarms, load_kpi
from .diagnosis_engine import diagnose_alarm
from .retriever import FaultRetriever
from .schemas import WorkflowStep, WorkflowTrace
from .ticket_generator import generate_ticket


CONSTRAINTS = [
    "mock_data_only",
    "no_network_required",
    "no_secrets",
    "resume_project_positioning_ai_application_agent_aiops",
]


def run_agent_workflow(alarm_id: str | None = None) -> WorkflowTrace:
    kpi_df = load_kpi()
    alarms_df = load_alarms()
    anomaly_df = detect_anomalies(kpi_df)

    if alarm_id is None:
        alarm = alarms_df.iloc[0].to_dict()
    else:
        matches = alarms_df[alarms_df["alarm_id"] == alarm_id]
        if matches.empty:
            raise ValueError(f"alarm_id not found: {alarm_id}")
        alarm = matches.iloc[0].to_dict()

    alarm_time = alarm["timestamp"]
    cell_context = get_cell_context(anomaly_df, str(alarm["cell_id"]), alarm_time)
    steps: list[WorkflowStep] = [
        WorkflowStep(
            agent="Monitor Agent",
            goal="Collect alarm and KPI context.",
            inputs=[str(alarm["alarm_id"]), str(alarm["cell_id"])],
            evidence=[
                f"{len(cell_context)} KPI rows in context window",
                f"{int(cell_context['has_anomaly'].sum())} rows contain at least one anomaly",
            ],
            output="KPI context prepared",
            verification="context window is non-empty",
        )
    ]

    query = f"{alarm['alarm_type']} {alarm['description']} {alarm['severity']}"
    hits = FaultRetriever().search(query, top_k=3)
    steps.append(
        WorkflowStep(
            agent="Knowledge Agent",
            goal="Retrieve relevant fault manual snippets.",
            inputs=[query],
            evidence=[f"{hit.source}:{hit.score}" for hit in hits],
            output=f"{len(hits)} knowledge snippets retrieved",
            verification="retriever returned ranked local snippets",
        )
    )

    diagnosis = diagnose_alarm(alarm, cell_context, hits)
    steps.append(
        WorkflowStep(
            agent="Diagnosis Agent",
            goal="Combine alarm, KPI evidence, rules, and knowledge snippets.",
            inputs=[diagnosis.alarm_type, diagnosis.cell_id],
            evidence=[
                f"root_cause={diagnosis.root_cause}",
                f"confidence={diagnosis.confidence}",
            ],
            output="DiagnosisResult generated",
            verification="diagnosis has root cause, confidence, evidence, and actions",
        )
    )

    ticket = generate_ticket(diagnosis)
    steps.append(
        WorkflowStep(
            agent="Ticket Agent",
            goal="Draft a structured operations ticket.",
            inputs=[diagnosis.alarm_id, diagnosis.root_cause],
            evidence=[ticket.priority, ticket.ticket_id],
            output=ticket.title,
            verification="ticket draft contains priority, summary, and recommended actions",
        )
    )

    trace = WorkflowTrace(
        alarm_id=diagnosis.alarm_id,
        constraints=CONSTRAINTS,
        steps=steps,
        diagnosis=diagnosis,
        ticket=ticket,
        verification="complete" if hits and diagnosis.kpi_evidence else "complete_with_assumptions",
    )
    return trace


def save_trace(trace: WorkflowTrace, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trace.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
