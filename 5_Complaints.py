import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )


# Download once
nltk.download("vader_lexicon")

st.set_page_config(
    page_title="Citizen Complaint AI",
    layout="centered"
)

st.title("🧠 Citizen Complaint AI")
st.caption("Automated sentiment analysis & priority routing for smart cities")

sia = SentimentIntensityAnalyzer()

# ---------------- SENTIMENT LOGIC ----------------
def analyze_sentiment(text):
    score = sia.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "positive", "low"
    elif score <= -0.05:
        return "negative", "high"
    else:
        return "neutral", "medium"

# ---------------- DB INSERT ----------------
def insert_complaint(city, category, department, text, sentiment, priority):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO citizen_complaints
        (city, category, department, complaint_text, sentiment, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (city, category, department, text, sentiment, priority))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- UI ----------------
st.subheader("📌 Register Complaint")

city = st.selectbox(
    "City",
    ["Chennai", "Delhi", "Bangalore", "Hyderabad", "Mumbai"]
)

category = st.selectbox(
    "Category",
    ["Water", "Road", "Electricity", "Garbage", "Traffic"]
)

department = st.text_input(
    "Department",
    value=f"{category} Department"
)

complaint_text = st.text_area(
    "Complaint Description",
    height=120
)

submit = st.button("🚀 Submit Complaint")

# ---------------- PROCESS ----------------
if submit:
    if complaint_text.strip() == "":
        st.error("Complaint description cannot be empty")
    else:
        sentiment, priority = analyze_sentiment(complaint_text)

        insert_complaint(city, category, department, complaint_text, sentiment, priority)

        st.success("✅ Complaint successfully registered")

        st.markdown("### 📊 Analysis Result")
        st.metric("Sentiment", sentiment.upper())
        st.metric("Priority Level", priority.upper())