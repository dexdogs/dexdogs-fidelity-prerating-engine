import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pypdf import PdfReader

st.set_page_config(page_title="dexdogs | Ratings Engine", layout="wide")

# --- APP STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { border: 1px solid #444; padding: 15px; border-radius: 12px; background-color: #161b22; }
    [data-testid="stMetricValue"] { color: white !important; }
    [data-testid="stMetricLabel"] { color: #888 !important; }
    .stFileUploader { padding: 20px; border: 1px dashed #444; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 dexdogs: Carbon Fidelity Engine")
st.caption("Predicting AAA-D Market Ratings: Manual Simulation & AI EPD Analysis")

# --- GLOBAL VARIABLES ---
score_audit = 0
score_source = 0
score_freq = 0
project_type = "N/A"
audit_label = "N/A"
source_label = "N/A"
is_manual = False

# --- SIDEBAR: INPUT METHOD SELECTION ---
with st.sidebar:
    st.header("🎛️ Input Configuration")
    input_mode = st.radio("Select Data Input Mode:", ["Manual Entry", "AI EPD Analysis"])
    
    st.divider()

    if input_mode == "Manual Entry":
        is_manual = True
        st.subheader("Manual Parameters")
        project_type = st.selectbox("Project Type", 
                                  ["Biochar", "Afforestation (ARR)", "Renewable Energy", "Concrete/Construction"])
        
        # Data Source (The 'BeZero' Factor)
        source_input = st.selectbox("Data Source Type", 
                                   ["A. Direct Sensor (IoT) / Remote Sensing", 
                                    "B. Metered / Hybrid Data", 
                                    "C. Engineering Estimates / Secondary"], index=2)
        if "Sensor" in source_input: 
            score_source = 40
            source_label = "A. Direct Sensor (Primary)"
        elif "Metered" in source_input: 
            score_source = 10
            source_label = "B. Metered (Hybrid)"
        else: 
            score_source = -10
            source_label = "C. Estimates (Secondary)"

        # Verification (The 'Sylvera' Factor)
        audit_input = st.selectbox("Verification Level", 
                                  ["L3: Reasonable Assurance (ISO 14064-3)", 
                                   "L2: Limited Assurance / Self-Declared", 
                                   "L1: Unverified"], index=2)
        if "Reasonable" in audit_input: 
            score_audit = 30
            audit_label = "L3: Reasonable Assurance"
        elif "Limited" in audit_input: 
            score_audit = 15
            audit_label = "L2: Limited Assurance"
        else: 
            score_audit = -20
            audit_label = "L1: Unverified"

        # Frequency
        freq_input = st.slider("Data Granularity (Freq)", 0, 100, 20, help="0=Annual, 100=Real-time")
        score_freq = freq_input / 5

    else:
        # AI EPD ANALYSIS MODE
        is_manual = False
        st.subheader("📄 EPD Ingestion")
        uploaded_file = st.file_uploader("Upload EPD (PDF)", type="pdf")
        st.info("Upload a PDF to auto-extract fidelity attributes using AI text scanning.")

# --- EPD PARSING LOGIC ---
def analyze_epd(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text().lower()
    
    # 1. DETECT PROJECT
    p_type = "General Construction"
    if "concrete" in text or "cement" in text: p_type = "Concrete / Cement"
    elif "glass" in text: p_type = "Glass Manufacturing"
    elif "steel" in text: p_type = "Metals / Steel"
    
    # 2. DETECT VERIFICATION
    if "third party verified" in text or "external verification" in text:
        a_lbl = "L3: Third-Party Verified (ISO 14025)"
        a_scr = 30
    elif "iso 14040" in text or "iso 14044" in text:
        a_lbl = "L2: Self-Declared (ISO Compliant)"
        a_scr = 15
    else:
        a_lbl = "L1: Unverified / Internal Estimate"
        a_scr = -20

    # 3. DETECT SOURCE
    if "primary data" in text or "site-specific" in text:
        s_lbl = "A. Direct Facility Data (Primary)"
        s_scr = 40
    elif "secondary data" in text or "database" in text:
        s_lbl = "C. Industry Average (Secondary)"
        s_scr = -10
    else:
        s_lbl = "B. Hybrid / Mixed Data"
        s_scr = 10
        
    return p_type, a_lbl, a_scr, s_lbl, s_scr

# --- MAIN EXECUTION ---
run_dashboard = False

if input_mode == "AI EPD Analysis" and uploaded_file is not None:
    with st.spinner("Scanning document for fidelity markers..."):
        project_type, audit_label, score_audit, source_label, score_source = analyze_epd(uploaded_file)
        score_freq = 5 # EPDs are usually static, so low frequency score
        run_dashboard = True
elif input_mode == "Manual Entry":
    run_dashboard = True

# --- DASHBOARD RENDER ---
if run_dashboard:
    # CALCULATE FINAL SCORES
    base_score = 40
    fidelity_score = min(max(base_score + score_audit + score_source + score_freq, 0), 100)
    
    # DETERMINE RATING
    if fidelity_score >= 80: rating, color, price = "AAA", "#00d4ff", 18.50
    elif fidelity_score >= 60: rating, color, price = "A", "#2ecc71", 14.20
    elif fidelity_score >= 40: rating, color, price = "BBB", "#f1c40f", 9.00
    else: rating, color, price = "D", "#c0392b", 2.50

    # SECTION 1: DATA INTELLIGENCE
    st.subheader(f"📂 Analysis: {project_type}")
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Data Source Strategy:**\n\n{source_label}")
    c2.success(f"**Verification Protocol:**\n\n{audit_label}")
    c3.warning(f"**Granularity Impact:**\n\n{'+' if score_freq > 10 else ''}{score_freq:.0f} pts")
    
    st.divider()

    # SECTION 2: THE RATING ENGINE
    row2_col1, row2_col2 = st.columns([1, 2])
    with row2_col1:
        st.metric("Predicted Market Rating", rating, delta="High Fidelity" if fidelity_score > 70 else "Information Risk")
        st.metric("Est. Credit Price", f"${price:.2f}", delta="Premium" if price > 10 else "Discount")
        st.metric("Fidelity Score", f"{fidelity_score}/100")

    with row2_col2:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = fidelity_score,
            title = {'text': "BeZero/Sylvera Fidelity Confidence"},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': "white"},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': '#333'},
                    {'range': [40, 70], 'color': '#555'},
                    {'range': [70, 100], 'color': '#777'}],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 80}
            }
        ))
        fig.update_layout(paper_bgcolor="#0e1117", font={'color': "white"}, height=300, margin=dict(t=30,b=30))
        st.plotly_chart(fig, use_container_width=True)

    # SECTION 3: GAP ANALYSIS & ADVICE
    st.subheader("💡 Fidelity Optimization")
    if fidelity_score < 80:
        st.write("To achieve **AAA** status and unlock the price premium, dexdogs recommends:")
        if score_source < 20:
            st.markdown("- **Deploy Sensors:** Move from 'Estimates' to 'Direct Measurement' (+30 pts).")
        if score_audit < 20:
            st.markdown("- **Audit Upgrade:** Secure ISO 14064-3 Reasonable Assurance (+20 pts).")
    else:
        st.success("Configuration meets Top-Tier market fidelity standards.")

else:
    # IDLE STATE
    st.info("👈 Select an input method in the sidebar to begin.")
    st.markdown("""
    ### dexdogs Fidelity Engine Modes:
    1.  **Manual Entry**: Simulate how changes in audit levels and sensors impact your credit rating.
    2.  **AI EPD Analysis**: Upload a PDF to automatically extract fidelity markers and predict pricing.
    """)
