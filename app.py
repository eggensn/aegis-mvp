import time
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Aegis Investigator", layout="wide")

# --- Synthetic in-code dataset (case queue) ---
SYNTHETIC_ENTITIES = {
    "CUST-1047": {
        "type": "Import/export business",
        "internal_flag_reason": "Unusual trade payments",
        "internal_risk": "High",
        "matching_banks": 3,               # Stage 1: match found at 3 other banks
        "anonymous_confirmations": 2,     # Stage 2: positive anonymous attestations
        "aggregate_risk": "High",
        "transactions": [
            {"from": "CUST-1047", "to": "Entity A", "amount": 25000, "note": "trade payments"},
            {"from": "Entity A", "to": "Account B", "amount": 24000, "note": "circular transfer"},
            {"from": "Account B", "to": "Entity C", "amount": 23000, "note": "repeat payments"},
        ],
    },
    "CUST-2198": {
        "type": "Individual customer",
        "internal_flag_reason": "Rapid incoming and outgoing transfers",
        "internal_risk": "Medium",
        "matching_banks": 0,               # Stage 1: no match -> stops
        "anonymous_confirmations": 0,
        "aggregate_risk": "Low",
        "transactions": [
            {"from": "CUST-2198", "to": "ACC-2198-1", "amount": 1200, "note": "single transfer"},
        ],
    },
    "CUST-3321": {
        "type": "SME",
        "internal_flag_reason": "Cash-intensive activity",
        "internal_risk": "High",
        "matching_banks": 1,               # Stage 1: match at 1 other bank
        "anonymous_confirmations": 1,      # Stage 2: confirmation but low aggregate risk
        "aggregate_risk": "Low",
        "transactions": [
            {"from": "CUST-3321", "to": "ACC-3321-1", "amount": 4000, "note": "cash flow"},
            {"from": "ACC-3321-1", "to": "ACC-3321-2", "amount": 3900, "note": "transfer"},
        ],
    },
}

# --- Session state for per-case workflow results ---
if "results" not in st.session_state:
    st.session_state["results"] = {}

def get_case_state(case_id):
    return st.session_state["results"].get(case_id, {
        "stage1_run": False, "stage1_pass": False,
        "stage2_run": False, "stage2_pass": False,
        "stage3_viewed": False
    })

def save_case_state(case_id, state):
    st.session_state["results"][case_id] = state

# --- Sidebar: case queue ---
st.sidebar.title("Case queue")
st.sidebar.markdown("Select case")

cases = list(SYNTHETIC_ENTITIES.keys())
selected = st.sidebar.selectbox("Select case", cases)
entity = SYNTHETIC_ENTITIES[selected]

st.sidebar.markdown("**Case summary**")
st.sidebar.write(f"- ID: {selected}")
st.sidebar.write(f"- Type: {entity['type']}")
st.sidebar.write(f"- Alert: {entity['internal_flag_reason']}")
st.sidebar.write(f"- Risk: {entity['internal_risk']}")
st.sidebar.markdown("---")
st.sidebar.caption("Bank Alpha · Investigations interface")

# --- Load case state ---
state = get_case_state(selected)

# --- Main header (product-like) ---
st.title("Aegis Investigator")
st.markdown("Investigation workspace · privacy-preserving review")

st.header(selected)
st.write(f"- Type: **{entity['type']}**")
st.write(f"- Bank Alpha alert reason: **{entity['internal_flag_reason']}**")
st.write(f"- Internal risk level: **{entity['internal_risk']}**")
st.markdown("---")

# --- Progress tracker (compact, product-like) ---
col1, col2, col3 = st.columns([1,1,1])

def render_stage(name, status, active=False):
    # status: "locked", "available", "completed", "failed"
    if status == "completed":
        icon = "✅"
        bg = "#e6ffed"
        border = "#2d8a4d"
    elif status == "failed":
        icon = "❌"
        bg = "#fff4e6"
        border = "#d97706"
    elif status == "available":
        icon = "⏳"
        bg = "#eef6ff" if active else "#ffffff"
        border = "#4c9aff" if active else "#e6eef8"
    else:
        icon = "🔒"
        bg = "#f5f7fa"
        border = "#d1d5db"
    html = f"""
    <div style="padding:10px;border-radius:8px;background:{bg};border:2px solid {border};text-align:center">
      <div style="font-size:18px">{icon} <strong>{name}</strong></div>
    </div>
    """
    return html

# Determine stage statuses using thresholds:
s1 = "locked"
s2 = "locked"
s3 = "locked"

# Stage 1 available initially
if not state["stage1_run"]:
    s1 = "available"
else:
    s1 = "completed" if state["stage1_pass"] else "failed"

# Stage 2 depends on Stage1 pass
if s1 == "completed":
    if not state["stage2_run"]:
        s2 = "available"
    else:
        s2 = "completed" if state["stage2_pass"] else "failed"
else:
    s2 = "locked"

# Stage 3 depends on Stage2 pass
if s2 == "completed":
    if not state["stage3_viewed"]:
        s3 = "available"
    else:
        s3 = "completed"
else:
    s3 = "locked"

active_stage = (
    1 if s1 == "available" else
    2 if s2 == "available" else
    3 if s3 == "available" else 0
)

col1.markdown(render_stage("Stage 1 — Consortium Match Check", s1, active=(active_stage==1)), unsafe_allow_html=True)
col2.markdown(render_stage("Stage 2 — Risk Attestation", s2, active=(active_stage==2)), unsafe_allow_html=True)
col3.markdown(render_stage("Stage 3 — Controlled Network View", s3, active=(active_stage==3)), unsafe_allow_html=True)

st.markdown("---")

# --- Stage cards (compact) ---
card1, card2, card3 = st.columns(3)

# Stage 1 card
with card1:
    st.subheader("Stage 1 — Consortium Match Check")
    st.write("Check whether this entity appears across the consortium.")
    st.info("Institution identities are not disclosed. Only the match count is returned.")
    matching = entity["matching_banks"]
    if state["stage1_run"]:
        st.write(f"- Match count: **{matching}**")
        if state["stage1_pass"]:
            st.success("Match confirmed — escalation available.")
        else:
            st.warning("No sufficient matches — escalation blocked.")
    run1 = st.button("Run match check", disabled=False)
    if run1:
        # simulate processing
        with st.spinner("Checking consortium matches..."):
            time.sleep(0.6)
        passed = matching >= 1  # threshold
        new_state = get_case_state(selected)
        new_state.update({"stage1_run": True, "stage1_pass": passed, "stage2_run": False, "stage2_pass": False, "stage3_viewed": False})
        save_case_state(selected, new_state)
        st.rerun()

# Stage 2 card
with card2:
    st.subheader("Stage 2 — Risk Attestation")
    st.write("Verify whether anonymous consortium risk signals exist for this entity.")
    st.info("Risk signals are aggregated and source institutions remain hidden.")
    locked2 = not (state["stage1_run"] and state["stage1_pass"])
    if state["stage2_run"]:
        confirmations = entity["anonymous_confirmations"]
        risk = entity["aggregate_risk"]
        st.write(f"- Anonymous confirmations: **{confirmations}**")
        st.write(f"- Aggregate risk: **{risk}**")
        if state["stage2_pass"]:
            st.success("Attestation verified — high-risk confirmed.")
        else:
            st.warning("Attestation received but risk not high enough.")
    run2 = st.button("Verify risk attestation", disabled=locked2)
    if run2:
        with st.spinner("Verifying attestation..."):
            time.sleep(0.6)
        confirmations = entity["anonymous_confirmations"]
        risk = entity["aggregate_risk"]
        passed2 = (confirmations >= 1) and (risk in ["High", "Critical"])
        new_state = get_case_state(selected)
        new_state.update({"stage2_run": True, "stage2_pass": passed2})
        new_state["stage3_viewed"] = False
        save_case_state(selected, new_state)
        st.rerun()

# Stage 3 card
with card3:
    st.subheader("Stage 3 — Controlled Network View")
    st.write("Review approved cross-institutional network indicators.")
    st.info("Network details are available only after prior-stage approval.")
    locked3 = not (state["stage1_run"] and state["stage1_pass"] and state["stage2_run"] and state["stage2_pass"])
    if state.get("stage3_viewed", False) and not locked3:
        st.success("Controlled network view opened.")
        df = pd.DataFrame(entity["transactions"])
        st.dataframe(df)
    run3 = st.button("Open controlled network view", disabled=locked3)
    if run3:
        new_state = get_case_state(selected)
        new_state["stage3_viewed"] = True
        save_case_state(selected, new_state)
        st.rerun()

st.markdown("---")

# --- Result summary (compact workspace) ---
left, right = st.columns(2)
with left:
    st.markdown("### Workflow status")
    st.write(f"- Stage 1: **{s1.capitalize()}**")
    st.write(f"- Stage 2: **{s2.capitalize()}**")
    st.write(f"- Stage 3: **{s3.capitalize()}**")
with right:
    st.markdown("### Case details")
    st.write(f"- ID: **{selected}**")
    st.write(f"- Type: **{entity['type']}**")
    st.write(f"- Alert: **{entity['internal_flag_reason']}**")
    st.write(f"- Internal risk: **{entity['internal_risk']}**")

st.markdown("---")
st.caption("Prototype environment · No live customer data")