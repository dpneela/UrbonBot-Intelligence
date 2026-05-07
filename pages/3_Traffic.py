import streamlit as st
import numpy as np
import os
from tensorflow.keras.models import load_model
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import smtplib
from email.message import EmailMessage

# ================= ENV =================
load_dotenv()

# ================= CONFIG =================
MODEL_PATH = "C:/db/models/traffic_lstm_model.h5"

# ================= DB CONNECTION =================
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )

# ================= EMAIL ALERT =================
def send_email_alert(subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = os.getenv("EMAIL_RECEIVER")
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(
                os.getenv("EMAIL_USER"),
                os.getenv("EMAIL_PASSWORD")
            )
            server.send_message(msg)

        return True
    except Exception:
        return False

# ================= LOAD MODEL =================
@st.cache_resource
def load_traffic_model():
    return load_model(MODEL_PATH, compile=False)

model = load_traffic_model()

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Traffic Forecasting", layout="wide")
st.title("🚦 Traffic Congestion Prediction System")
st.caption("LSTM-based traffic forecasting for proactive congestion management")

# ================= CITY / AREA =================
CITY_DATA = {
    "Chennai": ["Anna Nager", "Central", "T Nager", "Koyambedu"],
    "Delhi": ["Connaught Place", "Dwarka", "Saket"],
    "Bengaluru": ["Electronic City", "Whitefield", "Hebbal Flyover"],
    "Hyderabad": ["Hitech City", "Gachibowli", "Madhapur", "Kukatpally"],
    "Mumbai": ["Bandra Kurla Complex", "Andheri East", "Dadar"],
    
}

left, right = st.columns([1.1, 1])

# ================= INPUT =================
with left:
    st.subheader("📥 Input")

    city = st.selectbox("City", list(CITY_DATA.keys()))
    area = st.selectbox("Area", CITY_DATA[city])

    st.markdown("**Simulated recent traffic volume (last 60 time-steps)**")

    min_val, max_val = st.slider(
        "Vehicle Count Range",
        min_value=10,
        max_value=100,
        value=(20, 50)
    )

    predict_btn = st.button("📈 Predict Traffic")

# ================= OUTPUT =================
with right:
    st.subheader("📊 Output")

    if predict_btn:

        # Simulated 60-step input sequence
        input_series = np.random.randint(min_val, max_val, size=(60, 1))
        input_series = input_series / 100.0  # Normalize
        input_series = np.expand_dims(input_series, axis=0)

        predicted_value = model.predict(input_series)[0][0]
        predicted_traffic = int(predicted_value * 100)

        # Congestion logic (must match ENUM: low, medium, high)
        if predicted_traffic < 30:
            congestion = "low"
        elif predicted_traffic < 50:
            congestion = "medium"
        else:
            congestion = "high"

        st.metric("🚗 Predicted Vehicle Count", predicted_traffic)
        st.metric("🚦 Congestion Level", congestion.upper())

        # ================= SAVE TO DB =================
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO traffic_forecast
                (city, area, forecast_time,
                 predicted_vehicle_count, congestion_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                city,
                area,
                datetime.now(),
                predicted_traffic,
                congestion
            ))

            conn.commit()
            cursor.close()
            conn.close()

            st.success("✅ Traffic prediction saved to database")

        except Exception as e:
            st.error(f"❌ Database error: {e}")

        # ================= EMAIL ALERT =================
        if congestion == "high":

            email_body = f"""
🚦 TRAFFIC CONGESTION ALERT 🚦

City: {city}
Area: {area}
Predicted Vehicle Count: {predicted_traffic}
Congestion Level: HIGH

Suggested Actions:
• Signal timing optimization
• Route diversion
• Deploy traffic personnel

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            if send_email_alert("🚦 UrbanBot Traffic Alert", email_body):
                st.info("📧 Traffic alert sent successfully")

    else:
        st.info("Click 'Predict Traffic' to generate forecast.")