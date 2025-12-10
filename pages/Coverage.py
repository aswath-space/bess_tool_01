import streamlit as st
from ui.css import load_css

st.set_page_config(
    page_title="Data Coverage - Investor Guide Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css("assets/style.css")

st.title("Data Coverage & Supported Zones")

st.markdown("""
<div class="css-card">
    <h3>Supported Market Zones</h3>
    <p>We actively support data integration from the following sources:</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="css-card" style="text-align: left;">
        <h4>🇪🇺 ENTSO-E (Live API)</h4>
        <p>Real-time Day-Ahead Market Prices for most European countries.</p>
        <ul>
            <li>Germany (DE_LU)</li>
            <li>France (FR)</li>
            <li>Netherlands (NL)</li>
            <li>Spain (ES)</li>
            <li>...and 30+ others.</li>
        </ul>
        <br>
        <small class="text-slate-500">Source: ENTSO-E Transparency Platform</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="css-card" style="text-align: left;">
        <h4>📂 Offline Datasets (CSV)</h4>
        <p>Pre-loaded historical data for non-ENTSO-E regions or future scenarios.</p>
        <ul>
            <li><strong>FUTURE_GRID</strong> (Experimental Scenario)</li>
            <li><strong>DEMO_LAND</strong> (Hypothetical Market)</li>
        </ul>
        <br>
        <small class="text-slate-500">Source: Internal Research & Projections</small>
    </div>
    """, unsafe_allow_html=True)
