import os
import streamlit as st
import pymysql
from ultralytics import YOLO
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# ===============================
# CONFIG
# ===============================
MODEL_PATH = "C:/db/models/best.pt"
CONF_THRESHOLD = 0.25

# ===============================
# DB CONNECTION
# ===============================
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )

# ===============================
# LOAD MODEL
# ===============================
@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)

model = load_model()

# ===============================
# UI
# ===============================
st.set_page_config(page_title="Pothole Detection", layout="wide")
st.title("🛣️ Road Infrastructure – Pothole Detection")

CITY_DATA = {
    "Chennai": ["Anna Nager", "Central", "T Nager", "Koyambedu"],
    "Delhi": ["Connaught Place", "Dwarka", "Saket"],
    "Bengaluru": ["Electronic City", "Whitefield", "Hebbal Flyover"],
    "Hyderabad": ["Hitech City", "Gachibowli", "Madhapur", "Kukatpally"],
    "Mumbai": ["Bandra Kurla Complex", "Andheri East", "Dadar"],
}

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("City", CITY_DATA.keys())
    area = st.selectbox("Area", CITY_DATA[city])
    latitude = st.number_input("Latitude", value=13.0827)
    longitude = st.number_input("Longitude", value=80.2707)
    image_file = st.file_uploader("Upload Road Image", ["jpg","jpeg","png"])

with col2:
    st.subheader("Detection Preview")
    preview = st.empty()

# ===============================
# DETECTION LOGIC
# ===============================
if image_file and st.button("🔍 Detect Potholes"):

    img_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    results = model.predict(image, conf=CONF_THRESHOLD)
    boxes = results[0].boxes
    pothole_count = len(boxes)
    avg_conf = float(boxes.conf.mean()) if pothole_count > 0 else 0.0

    # Severity Logic
    if pothole_count == 0:
        severity = "minor"
    elif pothole_count <= 3:
        severity = "moderate"
    else:
        severity = "severe"

    # Display Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("🕳️ Potholes", pothole_count)
    c2.metric("📊 Confidence", f"{avg_conf:.2f}")
    c3.metric("⚠️ Severity", severity.upper())

    annotated = results[0].plot()
    preview.image(annotated, channels="BGR", use_container_width=True)

    # ===============================
    # INSERT INTO DATABASE
    # ===============================
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pothole_events
            (city, area, latitude, longitude,
             pothole_count, confidence_score, severity)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            city,
            area,
            latitude,
            longitude,
            pothole_count,
            avg_conf,
            severity
        ))

        conn.commit()
        conn.close()

        st.success("✅ Pothole data stored successfully")

    except Exception as e:
        st.error(f"Database error: {e}")

else:
    st.info("Upload an image and click Detect Potholes.")