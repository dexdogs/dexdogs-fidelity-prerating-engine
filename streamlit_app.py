import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pypdf import PdfReader

st.set_page_config(page_title="dexdogs | EPD Analyzer", layout="wide")

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
st.caption("AI-Powered EPD Analysis & Rating Prediction (BeZero/Sylvera Protocol)")

# --- SIDEBAR: UPLOAD ONLY ---
with st.sidebar:
    st.header("📄 Data Ingestion")
    uploaded_file = st.file_uploader("Upload EPD (PDF)", type="pdf")
    st.info("Upload an Environmental Product Declaration to auto-extract fidelity attributes.")

# --- ANALYSIS ENGINE ---
def analyze_epd(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text().lower()
    
    # 1. DETECT PROJECT TYPE
    project_type = "General Construction"
    if "concrete" in text or "cement" in text: project_type = "Concrete / Cement"
    elif "glass" in text or "glazing" in text: project_type = "Glass Manufacturing"
    elif "steel" in text or "aluminum" in text: project_type = "Metals / Steel"
    elif "wood" in text or "timber" in text: project_type = "Bio-Materials / Wood"
    
    # 2. DETECT VERIFICATION (The 'Sylvera' Factor)
    # Looking for ISO standards and verification bodies
    if "third party verified" in text or "external verification" in text:
        audit = "L3: Third-Party Verified (ISO 14025)"
        audit_score = 30
    elif "iso 14040" in text or "iso 14044" in text:
        audit = "L2: Self-Declared (ISO Compliant)"
        audit_score = 15
    else:
        audit = "L1: Unverified / Internal Estimate"
        audit_score = -20

    # 3. DETECT DATA SOURCE (The 'BeZero' Factor)
    # Looking for primary vs secondary data declarations
    if "primary data" in text or "site-specific" in text or "facility specific" in text:
        source = "A. Direct Facility Data (Primary)"
        source_score = 40
    elif "secondary data" in text or "database" in text or "generic" in text:
        source = "C. Industry Average (Secondary)"
        source_score = -10
    else:
        # Fallback if vague
        source = "B. Hybrid / Mixed Data"
        source_score = 10
        
    return project_type, audit, audit_score, source, source_score

# --- RATING CALCULATOR ---
def get_rating(total_score):
    if total_score >= 80: return "AAA", "#00d4ff", 18.50
    elif total_score >= 60: return "A", "#2ecc71", 14.20
    elif total_score >= 40: return "BBB", "#f1c40f", 9.00
    else: return "D", "#c0392b", 2.50

# --- MAIN INTERFACE ---
if uploaded_file is not None:
    # RUN ANALYSIS
    with st.spinner("Scanning document for fidelity markers..."):
        p_type, audit, a_score, source, s_score = analyze_epd(uploaded_file)
        
        # Calculate Final Fidelity Score (0-100)
        base_score = 40 # Starting baseline
        fidelity_score = min(max(base_score + a_score + s_score, 0), 100)
        rating, color, price = get_rating(fidelity_score)

    # --- SECTION 1: AUTO-EXTRACTED INTELLIGENCE ---
    st.subheader(f"📂 Analysis Results: {uploaded_file.name}")
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Project Detected:**\n\n{p_type}")
    c2.success(f"**Verification:**\n\n{audit}")
    c3.warning(f"**Data Source:**\n\n{source}")
    
    st.divider()

    # --- SECTION 2: THE RATING REVEAL ---
    row2_col1, row2_col2 = st.columns([1, 2])
    
    with row2_col1:
        st.metric("Predicted Market Rating", rating, delta="High Fidelity" if fidelity_score > 70 else "Information Risk")
        st.metric("Est. Credit Price", f"${price:.2f}", delta="Premium" if price > 10 else "Discount")
        st.metric("Fidelity Score", f"{fidelity_score}/100")
        
    with row2_col2:
        # GAUGE CHART
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = fidelity_score,
            title = {'text': "Data Fidelity Confidence"},
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
        fig.update_layout(paper_bgcolor="#0e1117", font={'color': "white"}, height=300)
        st.plotly_chart(fig, use_container_width=True)

    # --- SECTION 3: UPGRADE PATH ---
    if fidelity_score < 80:
        st.subheader("💡 Optimization Strategy")
        st.write("To achieve **AAA** status and increase value, dexdogs recommends:")
        if s_score < 20:
            st.markdown("- **Replace Secondary Data:** Integrate IoT sensors to capture 'Site-Specific' primary data.")
        if a_score < 20:
            st.markdown("- **Upgrade Verification:** Move from Self-Declared to Third-Party ISO 14025 verification.")

else:
    # IDLE STATE
    st.info("👈 Upload an EPD PDF in the sidebar to begin analysis.")
    st.markdown("""
    ### How dexdogs analyzes your data:
    1.  **Text Extraction**: We scan the EPD for specific ISO standards (e.g., *14025*, *14044*).
    2.  **Source Classification**: We distinguish between *Primary* (Sensor) and *Secondary* (Database) sources.
    3.  **Risk Modeling**: We apply the **BeZero/Sylvera** risk framework to predict your market rating.
    """)
