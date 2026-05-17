from __future__ import annotations

from pathlib import Path
import pandas as pd

from .config import DATA_DIR, KNOWLEDGE_DIR


def load_kpi(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "kpi.csv", parse_dates=["timestamp"])
    return df.sort_values(["cell_id", "timestamp"]).reset_index(drop=True)


def load_alarms(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "alarms.csv", parse_dates=["timestamp"])
    return df.sort_values("timestamp", ascending=False).reset_index(drop=True)


def load_tickets(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(data_dir / "tickets.csv")


def load_knowledge_documents(knowledge_dir: Path = KNOWLEDGE_DIR) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs
