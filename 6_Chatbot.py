import streamlit as st
import pymysql
import os
from dotenv import load_dotenv
from groq import Groq

# ================= LOAD ENV =================
load_dotenv()

# ================= GROQ CLIENT =================
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ================= DB CONNECTION =================
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="urbanbot"
    )

# ================= RETRIEVE DATA =================
def retrieve_city_context():
    conn = get_connection()
    cursor = conn.cursor()

    # High congestion cities
    cursor.execute("""
        SELECT city, COUNT(*)
        FROM traffic_forecast
        WHERE congestion_level='high'
        GROUP BY city
    """)
    traffic_data = cursor.fetchall()

    # High priority complaints
    cursor.execute("""
        SELECT COUNT(*)
        FROM citizen_complaints
        WHERE priority='high'
    """)
    complaints = cursor.fetchone()[0]

    # Latest AQI
    cursor.execute("""
    SELECT city, aqi, aqi_category
    FROM air_quality_forecast
    ORDER BY created_at DESC  
    LIMIT 1
""")
    aqi = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "traffic": traffic_data,
        "complaints": complaints,
        "aqi": aqi
    }

# ================= BUILD SYSTEM PROMPT =================
def build_system_prompt(context):
    return f"""
You are UrbanBot, a Smart City AI assistant.

Use ONLY the provided data below to answer questions.

City Data:
- High Traffic Records: {context['traffic']}
- High Priority Complaints: {context['complaints']}
- Latest AQI: {context['aqi']}

Rules:
- Do not hallucinate.
- Base answers strictly on provided data.
- Provide analytical insights and recommendations.
"""

# ================= GENERATE RESPONSE =================
def generate_response(user_query, system_prompt):

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",   # ✅ WORKING MODEL
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# ================= STREAMLIT UI =================
st.set_page_config(page_title="UrbanBot GROQ RAG", layout="wide")
st.title("🤖 UrbanBot GROQ RAG Assistant")
st.caption("Retrieval-Augmented Smart City Decision Support System")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask about traffic, AQI, complaints...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    context = retrieve_city_context()
    system_prompt = build_system_prompt(context)
    reply = generate_response(user_input, system_prompt)

    st.session_state.chat_history.append(("assistant", reply))

for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(message)