from __future__ import annotations

from .schemas import DiagnosisResult, TicketDraft


def priority_from_diagnosis(diagnosis: DiagnosisResult) -> str:
    if diagnosis.severity == "critical" or diagnosis.confidence >= 0.85:
        return "P1"
    if diagnosis.severity == "major" or diagnosis.confidence >= 0.7:
        return "P2"
    return "P3"


def generate_ticket(diagnosis: DiagnosisResult) -> TicketDraft:
    priority = priority_from_diagnosis(diagnosis)
    title = f"[{priority}] {diagnosis.cell_id} {diagnosis.alarm_type}: {diagnosis.root_cause}"
    evidence_lines = [
        f"{item['kpi']}={item['value']} z={item['z_score']} status={item['status']}"
        for item in diagnosis.kpi_evidence
    ]
    summary = (
        f"Alarm {diagnosis.alarm_id} on {diagnosis.cell_id} is likely caused by "
        f"{diagnosis.root_cause}. Confidence={diagnosis.confidence}. "
        f"Evidence: {'; '.join(evidence_lines) if evidence_lines else 'no KPI evidence'}."
    )
    return TicketDraft(
        ticket_id=f"TICKET-{diagnosis.alarm_id}",
        alarm_id=diagnosis.alarm_id,
        priority=priority,
        title=title,
        summary=summary,
        recommended_actions=diagnosis.recommended_actions,
    )
