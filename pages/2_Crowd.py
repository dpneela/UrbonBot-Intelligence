import os
import streamlit as st
import pymysql
import cv2
import numpy as np
from dotenv import load_dotenv
from tensorflow.keras.models import load_model

load_dotenv()

# ===============================
# CONFIG
# ===============================
MODEL_PATH = "C:/db/models/crowd_cnn_model.h5"

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
def load_crowd_model():
    return load_model(MODEL_PATH, compile=False)

model = load_crowd_model()

# ===============================
# UI
# ===============================
st.set_page_config(page_title="Crowd Monitoring", layout="wide")
st.title("👥 Crowd Density Monitoring System")

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
    image_file = st.file_uploader("Upload Crowd Image", ["jpg","jpeg","png"])

with col2:
    st.subheader("Preview")
    preview = st.empty()

# ===============================
# DETECTION LOGIC
# ===============================
if image_file and st.button("📊 Estimate Crowd"):

    img_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    # --- Preprocess (adjust size to what your model expects) ---
    resized = cv2.resize(image, (224, 224))
    normalized = resized / 255.0
    input_image = np.expand_dims(normalized, axis=0)

    # --- Prediction ---
    prediction = model.predict(input_image)
    predicted_count = int(prediction[0][0])

    # --- Density Logic ---
    if predicted_count < 20:
        density = "low"
    elif predicted_count < 50:
        density = "medium"
    else:
        density = "high"

    risk_score = predicted_count / 100

    # --- Display ---
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Estimated Count", predicted_count)
    c2.metric("📈 Density Level", density.upper())
    c3.metric("⚠️ Risk Score", f"{risk_score:.2f}")

    preview.image(image, channels="BGR", use_container_width=True)

    # ===============================
    # INSERT INTO DATABASE
    # ===============================
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO crowd_density
            (city, area, latitude, longitude,
             estimated_count, density_level, risk_score)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            city,
            area,
            latitude,
            longitude,
            predicted_count,
            density,
            risk_score
        ))

        conn.commit()
        conn.close()

        st.success("✅ Crowd data stored successfully")

    except Exception as e:
        st.e