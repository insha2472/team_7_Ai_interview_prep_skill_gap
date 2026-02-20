from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

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
    print(f"Connecting to database...")
    with engine.connect() as conn:
        dialect = engine.dialect.name
        
        # 1. Fix 'users' table
        for col_name, col_type in columns_to_add:
            try:
                exists = False
                if dialect == "postgresql":
                    check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='{col_name}'")
                    exists = bool(conn.execute(check_sql).fetchone())
                elif dialect == "sqlite":
                    check_sql = text(f"PRAGMA table_info(users)")
                    result = conn.execute(check_sql).fetchall()
                    exists = any(row[1] == col_name for row in result)
                
                if not exists:
                    print(f"Adding column {col_name} to users...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                else:
                    print(f"Column {col_name} already exists in users.")
            except Exception as e:
                print(f"Error adding {col_name} to users: {e}")
        
        # 2. Fix 'test_results' table
        try:
            exists = False
            if dialect == "postgresql":
                check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='test_results' AND column_name='test_type'")
                exists = bool(conn.execute(check_sql).fetchone())
            elif dialect == "sqlite":
                check_sql = text("PRAGMA table_info(test_results)")
                result = conn.execute(check_sql).fetchall()
                exists = any(row[1] == 'test_type' for row in result)
                
            if not exists:
                print("Adding column test_type to test_results...")
                col_spec = "VARCHAR(50)" if dialect == "postgresql" else "TEXT"
                conn.execute(text(f"ALTER TABLE test_results ADD COLUMN test_type {col_spec}"))
            else:
                print("Column test_type already exists in test_results.")
        except Exception as e:
            print(f"Error adding test_type to test_results: {e}")

        # 3. Fix 'skill_analyses' table
        try:
            exists = False
            if dialect == "postgresql":
                check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='skill_analyses' AND column_name='priority_skills'")
                exists = bool(conn.execute(check_sql).fetchone())
            elif dialect == "sqlite":
                check_sql = text("PRAGMA table_info(skill_analyses)")
                result = conn.execute(check_sql).fetchall()
                exists = any(row[1] == 'priority_skills' for row in result)
                
            if not exists:
                print("Adding column priority_skills to skill_analyses...")
                conn.execute(text("ALTER TABLE skill_analyses ADD COLUMN priority_skills TEXT"))
            else:
                print("Column priority_skills already exists in skill_analyses.")
        except Exception as e:
            print(f"Error adding priority_skills to skill_analyses: {e}")

        conn.commit()
    print("Database schema fix completed.")

if __name__ == "__main__":
    fix_schema()
