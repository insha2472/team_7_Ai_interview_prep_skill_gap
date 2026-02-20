import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.getcwd(), ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Inspecting DB at: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

def inspect_db():
    tables = ["users", "test_results", "skill_analyses", "progress", "project_progress"]
    with engine.connect() as conn:
        dialect = engine.dialect.name
        print(f"Dialect: {dialect}")
        
        for table in tables:
            print(f"\n--- Table: {table} ---")
            try:
                if dialect == "postgresql":
                    sql = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
                else:
                    sql = text(f"PRAGMA table_info({table})")
                
                rows = conn.execute(sql).fetchall()
                for row in rows:
                    if dialect == "postgresql":
                        print(f"Column: {row[0]}, Type: {row[1]}")
                    else:
                        print(f"Column: {row[1]}, Type: {row[2]}")
            except Exception as e:
                print(f"Error inspecting {table}: {e}")

if __name__ == "__main__":
    inspect_db()
