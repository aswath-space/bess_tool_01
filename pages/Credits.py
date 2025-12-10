import streamlit as st
from ui.css import load_css

# --- Page Config ---
st.set_page_config(
    page_title="Credits - Investor Guide Tool",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

load_css("assets/style.css")

st.title("Credits & References")

st.markdown("""
<div class="css-card">
    <h3>Project Information</h3>
    <p>This tool was built to help investors analyze the financial viability of PV + BESS assets.</p>
    <br>
    <h4>Tech Stack & Data Sources</h4>
    <ul>
        <li><strong>Frontend:</strong> Streamlit</li>
        <li><strong>Data Processing:</strong> Pandas</li>
        <li><strong>Market Data:</strong> ENTSO-E Transparency Platform</li>
        <li><strong>Solar Simulation:</strong> PVGIS API</li>
    </ul>
</div>

<div class="css-card">
    <h3>References</h3>
    <p>The following resources were used in the development of this project:</p>
    
    <div style="padding: 1rem; border: 1px dashed #cbd5e1; border-radius: 8px; margin-top: 1rem;">
        <p><strong>Legacy Codebase References:</strong></p>
        <ul>
            <li>
                <a href="#" style="color: #2563eb; text-decoration: none;">📄 Original Implementation Specs (Placeholder)</a>
                <br>
                <span style="font-size: 0.9em; color: #64748b;">(Previously located in Reference/OtherCodes)</span>
            </li>
            <li style="margin-top: 0.5rem;">
                <a href="#" style="color: #2563eb; text-decoration: none;">📄 Product Requirements Document (Placeholder)</a>
                <br>
                <span style="font-size: 0.9em; color: #64748b;">(Previously located in Reference/PRD)</span>
            </li>
        </ul>
    </div>
</div>

<div class="css-card">
    <h3>Created By</h3>
    <p>Developed with ❤️ by the Investor Guide Team.</p>
</div>
""", unsafe_allow_html=True)
