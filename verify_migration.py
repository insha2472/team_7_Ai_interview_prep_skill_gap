from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if column exists
        check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='test_results' AND column_name='test_type'")
        result = conn.execute(check_sql).fetchone()
        
        if not result:
            print("RUNNING_MIGRATION")
            conn.execute(text("ALTER TABLE test_results ADD COLUMN test_type VARCHAR(50)"))
            conn.commit()
            print("MIGRATION_SUCCESS")
        else:
            print("COLUMN_ALREADY_EXISTS")
except Exception as e:
    print(f"ERROR: {e}")
