import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = r"d:\repos\team_7_Ai_interview_prep_skill_gap"
load_dotenv(os.path.join(backend_dir, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

def check_columns(table_name):
    print(f"\nChecking table: {table_name}")
    try:
        with engine.connect() as conn:
            if "sqlite" in DATABASE_URL:
                result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                cols = [row[1] for row in result]
                print(f"Columns: {cols}")
            else:
                result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")).fetchall()
                cols = [row[0] for row in result]
                print(f"Columns: {cols}")
    except Exception as e:
        print(f"Error checking {table_name}: {e}")

check_columns("users")
check_columns("test_results")
