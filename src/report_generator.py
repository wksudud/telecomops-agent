from __future__ import annotations

from .schemas import WorkflowTrace


def generate_daily_report(traces: list[WorkflowTrace]) -> str:
    lines = ["# TelecomOps Daily Diagnosis Report", ""]
    lines.append(f"Diagnosed alarms: {len(traces)}")
    for trace in traces:
        d = trace.diagnosis
        lines.extend(
            [
                "",
                f"## {d.alarm_id} / {d.cell_id} / {d.alarm_type}",
                f"- Severity: {d.severity}",
                f"- Likely root cause: {d.root_cause}",
                f"- Confidence: {d.confidence}",
                f"- Ticket: {trace.ticket.ticket_id} ({trace.ticket.priority})",
                "- Actions:",
            ]
        )
        lines.extend([f"  - {action}" for action in d.recommended_actions])
    return "\n".join(lines)
