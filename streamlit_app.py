import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/entso.env')

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import custom UI modules
# Import custom UI modules
from ui.css import load_css
from ui.inputs import render_inputs
from ui.results import render_results

# Import Backend Services
# We wrap imports in try-except to handle potential path issues gracefully
try:
    from app.services.entsoe_service import entsoe_service
    from app.services.pv_service import pv_service
    from app.services.optimization_service import optimization_service
except ImportError as e:
    st.error(f"Critical Error: Could not import backend services. {e}")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Investor Guide Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Load Styles ---
load_css("assets/style.css")

# --- Header ---
st.title("PV-BESS Investor Guide")
st.markdown("""
<div class="css-card">
    <h3>Revenue Optimization Tool</h3>
    <p>Simulate the financial performance of your Solar Park + Battery Storage asset based on real historical market prices and solar irradiation data.</p>
</div>
""", unsafe_allow_html=True)

# --- Inputs ---
config, run_clicked = render_inputs()

# --- Main Logic ---
if run_clicked:
    with st.spinner("Initializing Digital Twin & Fetching Data..."):
        try:
            # 1. Fetch Market Data (Last 365 Days)
            end_date = pd.Timestamp.now(tz='UTC').normalize()
            start_date = end_date - pd.Timedelta(days=365)
            
            # Get Zone
            zone = entsoe_service.get_zone_from_lat_lon(config['lat'], config['lon'])
            if not zone:
                st.warning(f"Could not determine ENTSO-E zone for coordinates ({config['lat']}, {config['lon']}). Defaulting to 'DE_LU' (Germany).")
                zone = "DE_LU"
            else:
                st.info(f"Detected Market Zone: **{zone}**")
            
            # Fetch Prices
            status_text = st.empty()
            status_text.text("Fetching Day-Ahead Market Prices...")
            prices_df = entsoe_service.fetch_day_ahead_prices(zone, start_date, end_date)
            
            # Prepare price data for optimization service
            # Service expects list of dicts with 'price' key
            price_data = prices_df.reset_index().rename(columns={'index': 'timestamp', 'price': 'price'}).to_dict(orient='records')
            
            # 2. Fetch PV Data
            status_text.text("Simulating PV Generation (PVGIS)...")
            pv_df = pv_service.fetch_pv_generation(
                lat=config['lat'],
                lon=config['lon'],
                peak_power_kw=config['pv_capacity_mw'] * 1000,
                loss=14.0, # Default loss
                tilt=config['pv_tilt'],
                azimuth=config['pv_azimuth']
            )
            
            # 3. Run Optimization
            status_text.text("Running Optimization Algorithms...")
            result = optimization_service.run_optimization(
                pv_df=pv_df,
                price_data=price_data,
                bess_power_mw=config['bess_power_mw'],
                bess_capacity_mwh=config['bess_capacity_mwh']
            )
            
            status_text.empty() # Clear status
            st.success("Optimization Complete!")
            
            # 4. Render Results
            render_results(result, market_data_df=prices_df)
            
        except Exception as e:
            st.error(f"An error occurred during execution: {str(e)}")
else:
    # Empty State with Call to Action
    st.info("👈 Enter your project details in the sidebar and click 'Run Optimization' to start.")
    
    # Optional: Display generic market data preview or map here
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 1. Define Asset")
        st.caption("Configure the size and location of your solar park and battery storage.")
    with col2:
        st.markdown("#### 2. Market Data")
        st.caption("We fetch real hourly historical price data for the specific region.")
    with col3:
        st.markdown("#### 3. Optimize Revenue")
        st.caption("Our algorithm simulates intelligent battery dispatch to maximize revenue.")

