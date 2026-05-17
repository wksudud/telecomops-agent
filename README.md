# TelecomOps Agent

[中文文档](README.zh-CN.md) | English

A local, mock-data AI operations platform for telecom network fault diagnosis. Built as a resume-grade AI engineering project for a BUPT AI undergraduate targeting AI application development, AI Agent engineering, AIOps, SRE tooling, and telecom network intelligence roles.

This is not a traditional algorithm research project, education product, customer-service bot, or sales assistant.

## What This Proves

- **End-to-end AI system design**: the project stitches data pipelines, anomaly detection, information retrieval, rule-based reasoning, multi-agent orchestration, and structured output generation into one runnable system.
- **Domain-aware engineering**: choosing telecom network operations as the domain leverages BUPT's telecom/network curriculum — the KPIs, alarm types, fault categories, and diagnostic workflows reflect real NOC (Network Operations Center) concepts, not generic toy examples.
- **Agent workflow transparency**: every diagnosis produces a structured `WorkflowTrace` with per-agent goals, inputs, evidence, outputs, constraints, and verification fields — so the reasoning is auditable, not a black box.
- **Reproducible without external dependencies**: the demo runs entirely on local mock data with zero network calls, secrets, or paid APIs, making it suitable for interview screens and take-home project evaluations.

## Quick Start

```powershell
cd <project-root>
python scripts\generate_mock_data.py
python -B scripts\smoke_test.py
streamlit run app.py
```

The smoke test requires no network access or API keys. It diagnoses alarm `ALARM-1001` end-to-end and asserts confidence, KPI evidence, knowledge evidence, and ticket generation.

The Streamlit demo includes a sidebar language selector for English and Chinese.

## Architecture

```
Mock KPI/Alarm CSV + Fault Manuals
        |
        v
Data Loader -> Anomaly Detection -> Monitor Agent
        |                             |
        v                             v
TF-IDF Retriever -> Knowledge Agent -> Diagnosis Agent -> Ticket Agent
        |                                                   |
        v                                                   v
 Streamlit Dashboard                                WorkflowTrace JSON
```

### Agent Workflow

| Step | Agent | Role |
|------|-------|------|
| 1 | Monitor Agent | Collect alarm and KPI context from rolling z-score anomaly detection |
| 2 | Knowledge Agent | Retrieve relevant fault manual snippets via TF-IDF + cosine similarity |
| 3 | Diagnosis Agent | Combine alarm type, KPI evidence, rules, and knowledge into root-cause candidates with confidence |
| 4 | Ticket Agent | Draft a structured operations ticket with priority, summary, and recommended actions |

Each step records its goal, inputs, evidence, output, and a verifiable assertion in the workflow trace.

### Tech Stack

Python, Pandas, NumPy, Scikit-learn (TF-IDF), Streamlit, Plotly. Optional extension path: Chroma/FAISS for vector retrieval, OpenAI-compatible API for LLM-based diagnosis, FastAPI for REST endpoints.

## Project Structure

```
repo/
  app.py
  requirements.txt
  scripts/
    generate_mock_data.py
    smoke_test.py
  src/
    __init__.py
    agent_workflow.py
    anomaly_detection.py
    config.py
    data_loader.py
    diagnosis_engine.py
    report_generator.py
    retriever.py
    schemas.py
    ticket_generator.py
    visualization.py
  tests/
    run_tests.py
    test_agent_workflow.py
```

Generated demo data is written to `data/`, knowledge manuals to `knowledge_base/`, and smoke-test outputs to `artifacts/`.

## Resume Bullets

Choose bullets that match the role you're targeting. All claims are backed by running code in this repository.

**AI Application / Agent Engineer roles:**
- Designed and implemented a telecom AIOps Agent platform end-to-end: mock data generation, KPI anomaly detection (rolling z-score over 6 KPIs), local RAG-style fault knowledge retrieval (TF-IDF with cosine similarity over markdown manuals), rule-based root-cause diagnosis with confidence scoring, and automatic ticket/report generation.
- Built a multi-agent workflow trace system (Monitor, Knowledge, Diagnosis, Ticket) where every step records goal, inputs, evidence, output, and a verifiable assertion — making agent reasoning auditable rather than opaque.
- Delivered a Streamlit dashboard with Plotly visualizations that renders KPI charts, alarm severity distribution, anomaly heatmap, diagnosis evidence, cited knowledge snippets, and generated tickets in a single interactive view.

**AIOps / SRE Tooling roles:**
- Applied operational fault diagnosis patterns to telecom network data: alarm-to-KPI correlation, rolling baseline anomaly detection, knowledge-augmented root-cause analysis, and structured ticket drafting with priority classification.
- Designed the system to run deterministically on local mock data with no network access, secrets, or paid APIs — enabling reproducible demos for interview screens and take-home evaluations.

**Telecom Network Intelligence roles:**
- Demonstrated how AI engineering techniques (RAG, multi-agent orchestration, structured evidence logging) apply to telecom NOC workflows: KPI monitoring, fault manual retrieval, alarm diagnosis, and operations reporting — leveraging BUPT telecom and network curriculum as domain foundation.

## Interview Talking Points

- **Why telecom AIOps instead of a generic chatbot**: telecom is a systems-engineering domain with real operational data (KPIs, alarms, tickets, fault manuals) that maps naturally to AI patterns — retrieval, reasoning, structured output, and agent handoff. It also gives the interviewer a concrete mental model they can evaluate against their own experience. For a BUPT candidate, it directly connects academic background (communication networks, signal processing, network management) to AI application engineering.
- **Why deterministic rules and TF-IDF first, not LLM-first**: the MVP demonstrates the engineering scaffold — data pipeline, retrieval, diagnosis, workflow trace, dashboard — before adding an LLM. This order proves the candidate can design the system architecture and evidence model, not just prompt an API. The optional LLM adapter path is documented but not required for the demo.
- **What the workflow trace proves about Agent design**: every diagnosis includes per-agent goals, inputs, evidence, outputs, and verification fields. In an interview, you can walk through the trace JSON and show how each agent's reasoning is backed by concrete evidence — not a single opaque model call.
- **How the architecture extends to production**: the current local design maps to production components — Kafka for streaming KPIs and alarms, a vector DB (Chroma/PGVector) for knowledge retrieval, OpenTelemetry for observability, and OSS/NMS APIs for real data ingestion. The multi-agent trace pattern also maps to production Agent frameworks (LangGraph, AutoGen, CrewAI).

## Verification

```
python scripts/generate_mock_data.py
python -B scripts/smoke_test.py
python -B tests/run_tests.py
```

Optional: `python -m pytest -q` if pytest is installed.
