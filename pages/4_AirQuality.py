import streamlit as st
import pymysql
import pickle
import os
from datetime import datetime
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Air Quality Monitoring", layout="wide")
st.title("🌫️ Air Quality Index (AQI) Forecasting")
st.caption("ARIMA-based air quality forecasting for smart environmental management")

# ================= MODEL PATHS =================
AQI_MODELS = {
    "Chennai": "C:/db/models/aqi_arima_chennai.pkl"
}

AQI_STATIONS = {
    "Chennai": {
        "CAM-AQI-1": (13.0827, 80.2707)
    }
}

# ================= DB CONNECTION =================
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )

# ================= LOAD MODEL =================
@st.cache_resource
def load_arima_model(model_path):
    with open(model_path, "rb") as f:
        return pickle.load(f)

# ================= INPUT SECTION =================
left, right = st.columns([1.1, 1])

with left:
    st.subheader("📥 Input")

    city = st.selectbox("Select City", list(AQI_MODELS.keys()))
    station = st.selectbox(
        "Monitoring Station",
        list(AQI_STATIONS[city].keys())
    )

    latitude, longitude = AQI_STATIONS[city][station]

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Latitude", latitude, disabled=True)
    with c2:
        st.text_input("Longitude", longitude, disabled=True)

    forecast_days = st.slider(
        "Forecast Days",
        min_value=1,
        max_value=7,
        value=3
    )

    predict_btn = st.button("📊 Predict AQI")

# ================= OUTPUT SECTION =================
with right:
    st.subheader("📊 Output")

    if predict_btn:

        model = load_arima_model(AQI_MODELS[city])

        # Forecast next values
        forecast = model.forecast(steps=forecast_days)
        forecast = forecast.astype(int)

        predicted_aqi = int(forecast[-1])

        # ================= AQI CATEGORY LOGIC =================
        if predicted_aqi <= 50:
            category = "Good"
        elif predicted_aqi <= 100:
            category = "Moderate"
        elif predicted_aqi <= 200:
            category = "Poor"
        else:
            category = "Severe"

        st.metric("🌫️ Predicted AQI", predicted_aqi)
        st.metric("📌 Air Quality Category", category)

        # ================= SAVE TO DB =================
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
INSERT INTO air_quality_forecast
(city, area, forecast_time,
 pm25, pm10, aqi, aqi_category, created_at)
VALUES (%s, %s, %s,
        %s, %s, %s, %s, %s)
""", (
    city,
    station,                 # use station as area
    datetime.now(),          # forecast_time
    predicted_aqi,           # pm25
    predicted_aqi * 1.2,     # pm10
    predicted_aqi,           # aqi
    category,                # aqi_category
    datetime.now()           # created_at
))
            conn.commit()
            cursor.close()
            conn.close()

            st.success("✅ AQI forecast saved to database")

        except Exception as e:
            st.error(f"❌ DB error: {e}")

    else:
        st.info("Click 'Predict AQI' to generate forecast.")