from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

columns_to_add = [
    ("xp", "INTEGER DEFAULT 0"),
    ("level", "INTEGER DEFAULT 1"),
    ("xp_to_next", "INTEGER DEFAULT 500"),
    ("streak", "INTEGER DEFAULT 0"),
    ("earned_badges", "TEXT DEFAULT '[]'"),
    ("daily_xp", "TEXT DEFAULT '{}'"),
    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
]

def fix_schema():
    print(f"Connecting to {DATABASE_URL.split('@')[-1]}...")
    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                # PostgreSQL specific check if column exists
                check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='{col_name}'")
                result = conn.execute(check_sql).fetchone()
                
                if not result:
                    print(f"Adding column {col_name}...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                else:
                    print(f"Column {col_name} already exists.")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        
        conn.commit()
    print("Database schema fix completed.")

if __name__ == "__main__":
    fix_schema()
