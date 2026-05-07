import streamlit as st
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )

# -----------------------------
# FETCH METRICS
# -----------------------------
def fetch_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM traffic_forecast")
    traffic = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pothole_events")
    potholes = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(aqi) FROM air_quality_forecast")
    avg_aqi = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM crowd_density WHERE density_level='high'")
    high_crowd = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM citizen_complaints")
    complaints = cursor.fetchone()[0]

    conn.close()

    return traffic, potholes, avg_aqi, high_crowd, complaints

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="UrbanBot Dashboard", layout="wide")

st.title("🏙️ UrbanBot Intelligence – Smart City Control Center")

traffic, potholes, avg_aqi, high_crowd, complaints = fetch_metrics()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("🚑 Traffic", traffic)
col2.metric("🛣️ Potholes", potholes)
col3.metric("🌫️ Avg AQI", f"{avg_aqi:.1f}")
col4.metric("👥 High Crowd Zones", high_crowd)
col5.metric("📢 Complaints", complaints)

st.markdown("---")
st.info("Real-time AI-powered city monitoring dashboard.")