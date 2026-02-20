from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        print("Checking for priority_skills column...")
        try:
            # Check if column exists
            conn.execute(text("SELECT priority_skills FROM skill_analyses LIMIT 1"))
            print("Column priority_skills already exists.")
        except Exception:
            print("Adding priority_skills column to skill_analyses table...")
            conn.execute(text("ALTER TABLE skill_analyses ADD COLUMN priority_skills TEXT"))
            conn.commit()
            print("Column added successfully.")

if __name__ == "__main__":
    migrate()
