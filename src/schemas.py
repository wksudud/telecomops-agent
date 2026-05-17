from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class KnowledgeHit:
    source: str
    score: float
    snippet: str


@dataclass
class DiagnosisResult:
    alarm_id: str
    cell_id: str
    alarm_type: str
    severity: str
    root_cause: str
    confidence: float
    kpi_evidence: list[dict[str, Any]]
    knowledge_hits: list[KnowledgeHit]
    recommended_actions: list[str]
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["knowledge_hits"] = [asdict(hit) for hit in self.knowledge_hits]
        return data


@dataclass
class TicketDraft:
    ticket_id: str
    alarm_id: str
    priority: str
    title: str
    summary: str
    recommended_actions: list[str]
    status: str = "draft"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowStep:
    agent: str
    goal: str
    inputs: list[str]
    evidence: list[str]
    output: str
    verification: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowTrace:
    alarm_id: str
    constraints: list[str]
    steps: list[WorkflowStep]
    diagnosis: DiagnosisResult
    ticket: TicketDraft
    verification: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "alarm_id": self.alarm_id,
            "constraints": self.constraints,
            "steps": [step.to_dict() for step in self.steps],
            "diagnosis": self.diagnosis.to_dict(),
            "ticket": self.ticket.to_dict(),
            "verification": self.verification,
        }
