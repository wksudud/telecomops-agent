from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent_workflow import run_agent_workflow, save_trace
from src.report_generator import generate_daily_report


def ensure_data() -> None:
    required = [ROOT / "data" / "kpi.csv", ROOT / "data" / "alarms.csv", ROOT / "knowledge_base"]
    if all(path.exists() for path in required):
        return
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_mock_data.py")], check=True)


def main() -> None:
    ensure_data()
    trace = run_agent_workflow("ALARM-1001")
    if trace.diagnosis.confidence < 0.6:
        raise AssertionError(f"confidence too low: {trace.diagnosis.confidence}")
    if not trace.diagnosis.kpi_evidence:
        raise AssertionError("missing KPI evidence")
    if not trace.diagnosis.knowledge_hits:
        raise AssertionError("missing knowledge evidence")
    if not trace.ticket.title:
        raise AssertionError("missing ticket title")

    out_dir = ROOT / "artifacts"
    save_trace(trace, out_dir / "workflow_trace_ALARM-1001.json")
    report = generate_daily_report([trace])
    (out_dir / "daily_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(trace.to_dict(), ensure_ascii=False, indent=2)[:2500])
    print("SMOKE_TEST_PASS")


if __name__ == "__main__":
    main()
