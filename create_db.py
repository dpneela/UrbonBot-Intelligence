import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS urbanbot")

conn.commit()
conn.close()

print("Database 'urbanbot' created successfully")