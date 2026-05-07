import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MySQL
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="urbanbot"
)

cursor = conn.cursor()

# ==============================
# 1. POTHOLE EVENTS TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS pothole_events (
    pothole_id INT AUTO_INCREMENT PRIMARY KEY,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(50),
    area VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    pothole_count INT,
    confidence_score FLOAT,
    severity ENUM('minor','moderate','severe')
)
""")

# ==============================
# 2. CROWD DENSITY TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS crowd_density (
    crowd_id INT AUTO_INCREMENT PRIMARY KEY,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(50),
    area VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    estimated_count INT,
    density_level ENUM('low','medium','high'),
    risk_score FLOAT
)
""")

# ==============================
# 3. TRAFFIC FORECAST TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS traffic_forecast (
    forecast_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    area VARCHAR(100),
    forecast_time DATETIME,
    predicted_vehicle_count INT,
    congestion_level ENUM('low','medium','high'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ==============================
# 4. AIR QUALITY FORECAST TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS air_quality_forecast (
    aqi_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    area VARCHAR(100),
    forecast_time DATETIME,
    pm25 FLOAT,
    pm10 FLOAT,
    aqi INT,
    aqi_category ENUM('Good','Moderate','Poor','Severe'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ==============================
# 5. CITIZEN COMPLAINTS TABLE
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS citizen_complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(50),
    area VARCHAR(100),
    complaint_text TEXT,
    sentiment ENUM('positive','neutral','negative'),
    priority ENUM('low','medium','high')
)
""")

# Commit and close
conn.commit()
conn.close()

print("✅ UrbanBot minimal tables created successfully.")