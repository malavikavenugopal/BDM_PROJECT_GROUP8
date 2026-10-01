import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch variables
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # Connect to the database
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("Successfully connected to Supabase PostgreSQL database!")
    print("PostgreSQL Version:", record[0])
    cursor.close()
    connection.close()
except Exception as e:
    print("Connection error:", e)
