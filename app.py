import json

import streamlit as st

from src.agent_workflow import run_agent_workflow
from src.anomaly_detection import detect_anomalies
from src.data_loader import load_alarms, load_kpi
from src.visualization import alarm_severity_chart, anomaly_heatmap, available_kpis, kpi_line_chart


TEXT = {
    "en": {
        "language": "Language",
        "title": "TelecomOps Agent",
        "caption": "Mock telecom AIOps Agent demo for AI application, Agent engineering, AIOps, and SRE tooling roles.",
        "missing_data": "Demo data is missing. Run `python scripts/generate_mock_data.py` first.",
        "alarm_overview": "Alarm Overview",
        "anomaly_heatmap": "Anomaly Heatmap",
        "kpi_explorer": "KPI Explorer",
        "cell": "Cell",
        "kpi": "KPI",
        "diagnosis_workspace": "Alarm Diagnosis Workspace",
        "alarm": "Alarm",
        "root_cause": "Root Cause",
        "confidence": "Confidence",
        "ticket_priority": "Ticket Priority",
        "kpi_evidence": "KPI Evidence",
        "knowledge_evidence": "Knowledge Evidence",
        "ticket_draft": "Ticket Draft",
        "workflow_trace": "Agent Workflow Trace",
        "selected_alarm": "Selected alarm",
        "recommended_actions": "Recommended actions",
        "chart_alarm_severity": "Alarm severity distribution",
        "chart_anomaly_heatmap": "Anomaly count by cell and hour",
    },
    "zh": {
        "language": "语言",
        "title": "TelecomOps Agent 通信网络智能运维 Agent",
        "caption": "面向 AI 应用开发、Agent 工程、AIOps、SRE 工具和通信网络智能化岗位的本地模拟演示项目。",
        "missing_data": "演示数据缺失。请先运行 `python scripts/generate_mock_data.py`。",
        "alarm_overview": "告警概览",
        "anomaly_heatmap": "异常热力图",
        "kpi_explorer": "KPI 探索",
        "cell": "小区",
        "kpi": "KPI 指标",
        "diagnosis_workspace": "告警诊断工作台",
        "alarm": "告警",
        "root_cause": "可能根因",
        "confidence": "置信度",
        "ticket_priority": "工单优先级",
        "kpi_evidence": "KPI 证据",
        "knowledge_evidence": "知识库证据",
        "ticket_draft": "工单草稿",
        "workflow_trace": "Agent 工作流追踪",
        "selected_alarm": "当前告警",
        "recommended_actions": "建议动作",
        "chart_alarm_severity": "告警级别分布",
        "chart_anomaly_heatmap": "按小区和小时统计的异常数量",
    },
}

ROOT_CAUSE_ZH = {
    "radio interference or coverage degradation": "无线干扰或覆盖退化",
    "capacity congestion or transport bottleneck": "容量拥塞或传输瓶颈",
    "base station hardware, power, or transmission failure": "基站硬件、电源或传输故障",
    "core network path congestion or transport delay": "核心网路径拥塞或传输时延",
}

ACTION_ZH = {
    "Check recent radio parameter changes.": "检查近期无线参数变更。",
    "Inspect neighboring cell interference and handover relations.": "检查邻区干扰和切换关系。",
    "Prioritize drive-test or remote RF optimization for the affected cell.": "优先对受影响小区进行路测或远程射频优化。",
    "Check PRB utilization and active user count.": "检查 PRB 利用率和活跃用户数。",
    "Inspect transport link errors and backhaul congestion.": "检查传输链路错误和回传拥塞。",
    "Schedule capacity expansion if congestion is persistent.": "如果拥塞持续，安排容量扩容。",
    "Verify site power and RRU/BBU alarms.": "核查站点电源以及 RRU/BBU 告警。",
    "Check transmission status and site heartbeat.": "检查传输状态和站点心跳。",
    "Dispatch field engineer if remote recovery fails.": "远程恢复失败时派发现场工程师。",
    "Compare latency across neighboring cells.": "对比邻近小区时延。",
    "Inspect transport route and packet loss.": "检查传输路由和丢包情况。",
    "Escalate to core/transport team if multi-cell symptoms appear.": "若多小区同时出现症状，升级给核心网/传输团队。",
}


def translate_root_cause(value: str, lang: str) -> str:
    if lang == "zh":
        return ROOT_CAUSE_ZH.get(value, value)
    return value


def translate_actions(actions: list[str], lang: str) -> list[str]:
    if lang == "zh":
        return [ACTION_ZH.get(action, action) for action in actions]
    return actions


st.set_page_config(page_title="TelecomOps Agent", layout="wide")

lang_label = st.sidebar.selectbox("Language / 语言", ["English", "中文"], index=0)
lang = "zh" if lang_label == "中文" else "en"
t = TEXT[lang]

st.title(t["title"])
st.caption(t["caption"])

try:
    kpi_df = load_kpi()
    alarms_df = load_alarms()
except FileNotFoundError:
    st.warning(t["missing_data"])
    st.stop()

anomaly_df = detect_anomalies(kpi_df)

left, right = st.columns([1, 1])
with left:
    st.subheader(t["alarm_overview"])
    alarm_fig = alarm_severity_chart(alarms_df)
    alarm_fig.update_layout(title=t["chart_alarm_severity"])
    st.plotly_chart(alarm_fig, use_container_width=True)
with right:
    st.subheader(t["anomaly_heatmap"])
    heatmap_fig = anomaly_heatmap(anomaly_df)
    heatmap_fig.update_layout(title=t["chart_anomaly_heatmap"])
    st.plotly_chart(heatmap_fig, use_container_width=True)

st.subheader(t["kpi_explorer"])
cell_id = st.selectbox(t["cell"], sorted(kpi_df["cell_id"].unique()), index=2)
kpi = st.selectbox(t["kpi"], available_kpis(), index=0)
st.plotly_chart(kpi_line_chart(kpi_df, cell_id, kpi), use_container_width=True)

st.subheader(t["diagnosis_workspace"])
alarm_options = alarms_df["alarm_id"].tolist()
alarm_id = st.selectbox(t["alarm"], alarm_options)
alarm_row = alarms_df[alarms_df["alarm_id"] == alarm_id].iloc[0]
st.dataframe(alarms_df[alarms_df["alarm_id"] == alarm_id], use_container_width=True, hide_index=True)

trace = run_agent_workflow(alarm_id)
diag = trace.diagnosis
ticket = trace.ticket

metric_cols = st.columns(3)
metric_cols[0].metric(t["root_cause"], translate_root_cause(diag.root_cause, lang))
metric_cols[1].metric(t["confidence"], diag.confidence)
metric_cols[2].metric(t["ticket_priority"], ticket.priority)

st.markdown(f"### {t['kpi_evidence']}")
st.dataframe(diag.kpi_evidence, use_container_width=True)

st.markdown(f"### {t['knowledge_evidence']}")
for hit in diag.knowledge_hits:
    with st.expander(f"{hit.source} score={hit.score}", expanded=True):
        st.write(hit.snippet)

st.markdown(f"### {t['ticket_draft']}")
st.write(ticket.title)
st.write(ticket.summary)
st.markdown(f"**{t['recommended_actions']}**")
st.write(translate_actions(ticket.recommended_actions, lang))

st.markdown(f"### {t['workflow_trace']}")
st.json(json.dumps(trace.to_dict(), ensure_ascii=False))

st.caption(f"{t['selected_alarm']}: {alarm_row['description']}")
