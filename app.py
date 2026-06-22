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
        "matching_banks": 3,
        "anonymous_confirmations": 2,
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
        "matching_banks": 0,
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
        "matching_banks": 1,
        "anonymous_confirmations": 1,
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
    # include active_stage to control which stage panel is shown
    return st.session_state["results"].get(case_id, {
        "stage1_run": False, "stage1_pass": False,
        "stage2_run": False, "stage2_pass": False,
        "stage3_viewed": False,
        "active_stage": 1
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

# Ensure active_stage is valid given current pass/fail state
if state["stage1_run"] and (not state["stage1_pass"]) and state.get("active_stage",1) > 1:
    state["active_stage"] = 1
if state["stage2_run"] and (not state["stage2_pass"]) and state.get("active_stage",1) > 2:
    state["active_stage"] = 2

# --- Main header (product-like) ---
st.title("Aegis Investigator")
st.markdown("Investigation workspace · privacy-preserving review")

st.header(selected)
st.write(f"- Type: **{entity['type']}**")
st.write(f"- Bank Alpha alert reason: **{entity['internal_flag_reason']}**")
st.write(f"- Internal risk level: **{entity['internal_risk']}**")
st.markdown("---")

# --- Compact progress tracker ---
tracker_col1, tracker_col2, tracker_col3 = st.columns([1,1,1])

def render_stage_label(name, status, active=False):
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
    <div style="padding:8px;border-radius:6px;background:{bg};border:1.5px solid {border};text-align:center">
      <div style="font-size:15px">{icon} <strong style="font-size:14px">{name}</strong></div>
    </div>
    """
    return html

# compute statuses
s1 = "available" if not state["stage1_run"] else ("completed" if state["stage1_pass"] else "failed")
s2 = "locked"
if s1 == "completed":
    s2 = "available" if not state["stage2_run"] else ("completed" if state["stage2_pass"] else "failed")
s3 = "locked"
if s2 == "completed":
    s3 = "available" if not state["stage3_viewed"] else "completed"

active = state.get("active_stage", 1)
# normalize active to first available if current active is not allowed
if active == 2 and s2 == "locked":
    active = 1
if active == 3 and s3 == "locked":
    active = 1
state["active_stage"] = active
save_case_state(selected, state)

tracker_col1.markdown(render_stage_label("Stage 1 — Consortium Match Check", s1, active=(active==1)), unsafe_allow_html=True)
tracker_col2.markdown(render_stage_label("Stage 2 — Risk Attestation", s2, active=(active==2)), unsafe_allow_html=True)
tracker_col3.markdown(render_stage_label("Stage 3 — Controlled Network View", s3, active=(active==3)), unsafe_allow_html=True)

st.markdown("---")

# --- Main content: show only active stage panel ---
def show_stage1():
    st.subheader("Stage 1 — Consortium Match Check")
    st.write("Check whether this entity appears across the consortium.")
    st.info("Institution identities are not disclosed. Only the match count is returned.")
    matching = entity["matching_banks"]
    if state["stage1_run"]:
        st.write(f"- Match count: **{matching}**")
        if state["stage1_pass"]:
            st.success("Match confirmed — escalation available.")
            st.button("Continue to risk attestation", key="to_stage2", on_click=lambda: goto_stage(2))
        else:
            st.error("No sufficient matches — escalation blocked.")
    else:
        if st.button("Run match check"):
            with st.spinner("Checking consortium matches..."):
                time.sleep(0.6)
            passed = matching >= 1
            new_state = get_case_state(selected)
            new_state.update({"stage1_run": True, "stage1_pass": passed, "stage2_run": False, "stage2_pass": False, "stage3_viewed": False})
            # keep user on stage 1 after run; they can continue if passed
            new_state["active_stage"] = 1
            save_case_state(selected, new_state)
            st.rerun()

def show_stage2():
    st.subheader("Stage 2 — Risk Attestation")
    st.write("Verify whether anonymous consortium risk signals exist for this entity.")
    st.info("Risk signals are aggregated and source institutions remain hidden.")
    locked2 = not (state["stage1_run"] and state["stage1_pass"])
    if locked2:
        st.warning("Risk attestation is locked until consortium match is confirmed.")
        return
    if state["stage2_run"]:
        confirmations = entity["anonymous_confirmations"]
        risk = entity["aggregate_risk"]
        st.write(f"- Anonymous confirmations: **{confirmations}**")
        st.write(f"- Aggregate risk: **{risk}**")
        if state["stage2_pass"]:
            st.success("Attestation verified — high-risk confirmed.")
            st.button("Continue to controlled network view", key="to_stage3", on_click=lambda: goto_stage(3))
        else:
            st.error("Attestation received but risk not high enough — escalation stopped.")
    else:
        if st.button("Verify risk attestation"):
            with st.spinner("Verifying attestation..."):
                time.sleep(0.6)
            confirmations = entity["anonymous_confirmations"]
            risk = entity["aggregate_risk"]
            passed2 = (confirmations >= 1) and (risk in ["High", "Critical"])
            new_state = get_case_state(selected)
            new_state.update({"stage2_run": True, "stage2_pass": passed2})
            new_state["active_stage"] = 2
            new_state["stage3_viewed"] = False
            save_case_state(selected, new_state)
            st.rerun()

def show_stage3():
    st.subheader("Stage 3 — Controlled Network View")
    st.write("Review approved cross-institutional network indicators.")
    st.info("Network details are available only after prior-stage approval.")
    locked3 = not (state["stage1_run"] and state["stage1_pass"] and state["stage2_run"] and state["stage2_pass"])
    if locked3:
        st.warning("Controlled network view is locked until prior stages complete.")
        return
    if state.get("stage3_viewed", False):
        st.success("Controlled network view opened.")
        df = pd.DataFrame(entity["transactions"])
        st.dataframe(df)
    else:
        if st.button("Open controlled network view"):
            new_state = get_case_state(selected)
            new_state["stage3_viewed"] = True
            new_state["active_stage"] = 3
            save_case_state(selected, new_state)
            st.rerun()

def goto_stage(n):
    new_state = get_case_state(selected)
    # Only allow moving forward to available stages
    if n == 2 and (new_state["stage1_run"] and new_state["stage1_pass"]):
        new_state["active_stage"] = 2
    if n == 3 and (new_state["stage2_run"] and new_state["stage2_pass"]):
        new_state["active_stage"] = 3
    save_case_state(selected, new_state)
    st.rerun()

# show the active stage panel
active = get_case_state(selected).get("active_stage", 1)
if active == 1:
    show_stage1()
elif active == 2:
    show_stage2()
elif active == 3:
    show_stage3()

st.markdown("---")

# --- Compact status and case details ---
left, right = st.columns([1,1])
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