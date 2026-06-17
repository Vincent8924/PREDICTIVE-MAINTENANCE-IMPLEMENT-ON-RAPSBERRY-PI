"""
=============================================================================
Edge AI Predictive Maintenance Dashboard (ULTIMATE EDITION V2.1)
Framework: Streamlit & SQLite
Description: Fixed DuplicateWidgetID by using native st.rerun() for live updates.
Author: Vincent Tay Yong Jun
=============================================================================
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import time

# --- UI Configuration ---
st.set_page_config(page_title="AI Maintenance OS", layout="wide", page_icon="🏭")
st.title("🏭 Edge AI Predictive Maintenance Dashboard")
st.markdown("**Core Architecture: Lite-Hybrid-AE on Raspberry Pi 5**")

# =========================================================================
# DATABASE CONNECTION & DATA FETCHING
# =========================================================================
# Connect to the SQLite file (Ensure this file exists in the same directory)
conn = sqlite3.connect('vibration_data.db')

# Fetch the last 100 entries for the history table
df = pd.read_sql_query("SELECT * FROM logs_ultimate ORDER BY timestamp DESC LIMIT 100", conn)
conn.close()

if not df.empty:
    latest = df.iloc[0]
    status = latest['status']
    
    # ==========================================
    # MODULE 1: SYSTEM STATUS BANNER
    # ==========================================
    if "CALIBRATING" in status:
        st.info(f"⚙️ {status} (Dynamic Calibration in Progress...)")
    elif status == "NORMAL":
        st.success("🟢 MACHINE STATUS: NORMAL (Operational)")
    else:
        st.error("🔴 MACHINE STATUS: ANOMALY DETECTED (Alert!)")
    
    st.divider()
    
    # ==========================================
    # MODULE 2: KEY PERFORMANCE INDICATORS (KPIs)
    # ==========================================
    st.subheader("📊 Live AI & System Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("Current MSE", f"{latest['mse']:.4f}", f"Thresh: {latest['threshold']:.4f}")
    kpi2.metric("Peak Frequency", f"{latest['peak_freq']} Hz")
    kpi3.metric("Edge Latency", f"{latest['latency']} ms")
    kpi4.metric("CPU Temp", f"{latest['temp']} °C")
    
    # ==========================================
    # MODULE 3: EDGE HARDWARE HEALTH
    # ==========================================
    st.subheader("💻 Edge Gateway Health")
    h1, h2 = st.columns(2)
    h1.progress(int(latest['cpu']), text=f"CPU Usage: {latest['cpu']}%")
    h2.progress(int(latest['ram']), text=f"RAM Usage: {latest['ram']}%")
    
    st.divider()
    
    # ==========================================
    # MODULE 4: REAL-TIME OSCILLOSCOPE & TRENDS
    # ==========================================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📡 Live Vibration Waveform")
        if latest['raw_waveform']:
            waveform = json.loads(latest['raw_waveform'])
            st.line_chart(waveform, height=220)
    
    with col_right:
        st.subheader("📈 Anomaly Trend (MSE vs Limit)")
        # Reverse dataframe for chronological chart order
        trend_df = df.iloc[::-1].set_index('timestamp')[['mse', 'threshold']]
        st.line_chart(trend_df, height=220, color=["#1f77b4", "#d62728"])

    st.divider()

    # ==========================================
    # MODULE 5: HISTORICAL DATA LOG (The Table)
    # ==========================================
    st.subheader("📜 Historical Inference Logs")
    st.write("This table shows the persistent history stored in your local database.")
    
    # Drop the raw waveform column to keep the table clean
    display_df = df.drop(columns=['raw_waveform'])
    
    # Display the interactive table
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True
    )
    
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download History as CSV",
        data=csv,
        file_name='maintenance_history.csv',
        mime='text/csv',
        key='download_csv_btn' # Added a unique key for extra safety
    )

# =========================================================================
# THE MAGIC REFRESH ENGINE (Replaces the while loop)
# =========================================================================
# Pause for 1 second, then rerun the entire script from top to bottom
time.sleep(1)
st.rerun()