import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="dexdogs | Fidelity Pre-Rating Engine", layout="wide")

# --- CUSTOM CSS (Financial Terminal Look) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #161b22; border: 1px solid #333; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Fidelity Pre-Rating Engine // dexdogs")
st.caption("Predicting AAA-D Market Ratings based on Data Fidelity (BeZero/Sylvera Protocol)")

# --- SIDEBAR: INPUT YOUR CARBON DATA ---
with st.sidebar:
    st.header("1. Upload Project Data")
    # In a real Snowflake app, this would query your 'BENCHMARKS' table
    project_type = st.selectbox("Project Type", ["Biochar", "Afforestation (ARR)", "Renewable Energy", "Cookstoves"])
    
    st.header("2. Data Fidelity Profile")
    # These inputs determine the 'Information Risk' score
    data_source = st.selectbox("Data Source Type", 
                               ["A. Direct Sensor (IoT) / Remote Sensing", 
                                "B. Metered / Monthly Invoices", 
                                "C. Engineering Estimates / Manual Logs"], index=2)
    
    audit_level = st.selectbox("Verification Level", 
                               ["L3: Reasonable Assurance (ISO 14064-3)", 
                                "L2: Limited Assurance", 
                                "L1: Self-Reported / Unverified"], index=2)
    
    frequency = st.slider("Data Granularity (Update Frequency)", 0, 100, 20, help="0=Annual, 100=Real-time")

    if st.button("Run Pre-Rating Analysis"):
        run_analysis = True
    else:
        run_analysis = False

# --- RATING LOGIC ENGINE ---
def calculate_rating(source, audit, freq):
    # Base Score (0-100)
    score = 50 
    
    # 1. Source Fidelity Impact (The 'BeZero' Factor)
    if "Sensor" in source: score += 30
    elif "Metered" in source: score += 10
    else: score -= 15 # Penalty for estimates
    
    # 2. Audit Impact (The 'Sylvera' Factor)
    if "Reasonable" in audit: score += 15
    elif "Limited" in audit: score += 5
    else: score -= 20 # Severe penalty for unverified
    
    # 3. Frequency Bonus
    score += (freq / 5) # Up to +20 points for real-time data
    
    # Clamp score
    return min(max(score, 0), 100)

def get_rating_label(score):
    if score >= 90: return "AAA", "#00d4ff", 18.50 # Rating, Color, Est. Price
    elif score >= 80: return "AA", "#2ecc71", 14.20
    elif score >= 70: return "A", "#f1c40f", 11.00
    elif score >= 50: return "BBB", "#e67e22", 7.50
    elif score >= 30: return "BB", "#e74c3c", 4.00
    else: return "D", "#c0392b", 1.50

# --- DASHBOARD ---
if run_analysis:
    final_score = calculate_rating(data_source, audit_level, frequency)
    rating, color, price = get_rating_label(final_score)
    
    # TOP ROW: THE RATING REVEAL
    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Rating", rating, delta="High Fidelity" if final_score > 80 else "Info Risk Detected")
    c2.metric("Est. Market Price", f"${price:.2f}/tonne", delta=f"vs ${1.50:.2f} (Base)", delta_color="normal")
    c3.metric("Fidelity Score", f"{final_score:.0f}/100", delta="BeZero Protocol", delta_color="off")
    
    st.divider()
    
    # MIDDLE ROW: THE GAP ANALYSIS
    col_chart, col_advice = st.columns([2, 1])
    
    with col_chart:
        # Gauge Chart mimicking a Rating Agency Report
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = final_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Data Fidelity Confidence (AAA Standard)"},
            delta = {'reference': 90, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': '#333'},
                    {'range': [50, 80], 'color': '#555'},
                    {'range': [80, 100], 'color': '#777'}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        fig.update_layout(paper_bgcolor="#0e1117", font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)

    with col_advice:
        st.subheader("Rating Advisory")
        if final_score < 80:
            st.error(f"**Risk Factor:** Your reliance on {data_source.split(' ')[1]} data is capping your rating at {rating}.")
            st.info("**Fix:** Integrate real-time dMRV sensors to unlock AAA status and a potential +60% price premium.")
        else:
            st.success("**High Fidelity:** Your data structure aligns with Top-Tier rating methodologies.")

    # BOTTOM ROW: FINANCIAL IMPACT
    st.subheader("The Cost of Low Fidelity")
    # Comparing your credit vs Market Leaders
    data = {
        'Rating': ['D (Current)' if rating=='D' else 'D', 'BBB', 'A', 'AAA (Target)'],
        'Price': [1.50, 7.50, 11.00, 18.50],
        'Color': ['#c0392b', '#e67e22', '#f1c40f', '#00d4ff']
    }
    df = pd.DataFrame(data)
    fig_bar = px.bar(df, x='Rating', y='Price', color='Rating', 
                     title="Price Potential by Rating Notch",
                     color_discrete_map={k:v for k,v in zip(data['Rating'], data['Color'])})
    fig_bar.update_layout(template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.info("Configure your data sources in the sidebar to predict your Carbon Credit Rating.")
    st.markdown("""
    ### How it works
    1. **Data Ingestion**: We map your EPD/Sensor data to the **Sylvera/BeZero** risk framework.
    2. **Fidelity Scoring**: We penalize 'Estimated' data and reward 'Measured' data.
    3. **Rating Prediction**: We output the probable **AAA-D** rating before you submit to an agency.
    """)
