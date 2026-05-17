# TelecomOps Agent 通信网络智能运维 Agent

中文文档 | [English](README.md)

TelecomOps Agent 是一个基于本地模拟数据的通信网络智能运维项目，用于展示 KPI 异常检测、故障知识检索、根因诊断、多 Agent 工作流追踪和工单生成能力。项目面向 AI 应用开发、AI Agent 工程、AIOps、SRE 工具开发和通信网络智能化岗位。

它不是传统算法研究项目，不是教育产品，也不是客服、销售或售前工具。

## 这个项目证明什么

- **端到端 AI 工程能力**：把数据生成、异常检测、知识检索、规则推理、多 Agent 编排和结构化输出串成一个可运行系统。
- **通信领域结合能力**：用小区 KPI、告警、故障手册、工单等 NOC 场景元素，把北邮通信/网络背景转化成工程项目优势。
- **Agent 过程可审计**：每次诊断都会生成 `WorkflowTrace`，记录每个 Agent 的目标、输入、证据、输出、约束和验证结果。
- **无需外部服务即可复现**：项目只使用本地模拟数据，不需要网络、API Key 或付费模型，适合面试演示和简历项目评估。

## 快速开始

```powershell
cd <project-root>
python scripts\generate_mock_data.py
python -B scripts\smoke_test.py
streamlit run app.py
```

打开 Streamlit 后，可以在左侧选择 `English` 或 `中文`。  
smoke test 会对 `ALARM-1001` 完成一次端到端诊断，并校验置信度、KPI 证据、知识库证据和工单生成。

## 架构

```text
模拟 KPI/告警 CSV + 故障手册
        |
        v
数据加载 -> 异常检测 -> Monitor Agent
        |                         |
        v                         v
TF-IDF 检索 -> Knowledge Agent -> Diagnosis Agent -> Ticket Agent
        |                                                |
        v                                                v
 Streamlit 仪表盘                              WorkflowTrace JSON
```

### Agent 工作流

| 步骤 | Agent | 作用 |
|------|-------|------|
| 1 | Monitor Agent | 收集告警和 KPI 上下文，基于 rolling z-score 识别异常 |
| 2 | Knowledge Agent | 用 TF-IDF + 余弦相似度检索故障手册片段 |
| 3 | Diagnosis Agent | 结合告警类型、KPI 证据、规则和知识片段输出根因与置信度 |
| 4 | Ticket Agent | 生成结构化工单草稿，包括优先级、摘要和建议动作 |

每一步都会在 workflow trace 中记录目标、输入、证据、输出和验证说明。

## 技术栈

Python、Pandas、NumPy、Scikit-learn、Streamlit、Plotly。  
后续可以扩展 Chroma/FAISS 向量检索、OpenAI 兼容 LLM 诊断、FastAPI 接口和真实 OSS/NMS 数据接入。

## 项目结构

```text
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

生成的演示数据写入 `data/`，故障手册写入 `knowledge_base/`，smoke test 输出写入 `artifacts/`。这些目录默认被 `.gitignore` 忽略。

## 简历写法

**AI 应用 / Agent 工程方向：**

- 设计并实现通信网络 AIOps Agent 平台，集成模拟数据生成、6 项 KPI rolling z-score 异常检测、本地故障知识检索、规则化根因诊断、置信度评分和工单/日报生成。
- 构建 Monitor、Knowledge、Diagnosis、Ticket 四步 Agent 工作流追踪，每一步记录目标、输入、证据、输出和验证字段，使诊断过程可解释、可审计。
- 使用 Python、Pandas、Scikit-learn TF-IDF、Streamlit、Plotly 实现可复现本地 Demo，无需真实运营商数据、API Key 或付费模型。

**AIOps / SRE 工具方向：**

- 将告警-KPI 关联、滚动基线异常检测、知识增强诊断和结构化工单生成应用到通信网络运维场景，形成从告警到处置建议的闭环。
- 通过 smoke test、单元测试入口和 workflow trace 验证输出稳定性，适合作为面试演示和 take-home 项目。

**通信网络智能化方向：**

- 以通信网络小区 KPI、告警、故障手册和 NOC 工单为业务对象，展示 AI 工程方法在网络运维智能化中的落地方式。

## 面试讲法

- **为什么不是普通聊天机器人**：通信 AIOps 有清晰的数据结构和业务闭环，能展示数据处理、检索、诊断、工单、可视化和 Agent 编排能力。
- **为什么先用规则和 TF-IDF，而不是直接 LLM-first**：先构建可验证的工程骨架，避免把项目做成不可复现的 API 调用展示。
- **WorkflowTrace 的价值**：面试时可以打开 JSON，逐步解释每个 Agent 如何使用证据产生输出。
- **如何扩展到生产**：后续可接 Kafka、向量数据库、OpenTelemetry、OSS/NMS API、真实告警流和权限系统。

## 验证

```powershell
python scripts\generate_mock_data.py
python -B scripts\smoke_test.py
python -B tests\run_tests.py
```

如果安装了 pytest，也可以运行：

```powershell
python -m pytest -q
```
