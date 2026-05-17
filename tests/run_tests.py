from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent_workflow import run_agent_workflow


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_mock_data.py")], check=True)
    trace = run_agent_workflow("ALARM-1001")
    assert trace.diagnosis.alarm_id == "ALARM-1001"
    assert trace.diagnosis.confidence >= 0.6
    assert trace.diagnosis.kpi_evidence
    assert trace.diagnosis.knowledge_hits
    assert trace.ticket.ticket_id == "TICKET-ALARM-1001"
    assert len(trace.steps) == 4
    print("UNIT_TESTS_PASS")


if __name__ == "__main__":
    main()
