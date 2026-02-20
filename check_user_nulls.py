import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.getcwd(), ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_data():
    with engine.connect() as conn:
        print("--- Checking Users Profile Data ---")
        try:
            sql = text("SELECT id, name, email, xp, level, xp_to_next, streak FROM users")
            rows = conn.execute(sql).fetchall()
            for row in rows:
                print(f"\nUser: {row[1]} ({row[2]})")
                print(f"  xp: {row[3]}")
                print(f"  level: {row[4]}")
                print(f"  xp_to_next: {row[5]}")
                print(f"  streak: {row[6]}")
                
                nulls = [k for k,v in [("xp", row[3]), ("level", row[4]), ("xp_to_next", row[5]), ("streak", row[6])] if v is None]
                if nulls:
                    print(f"  !!! NULL FIELDS FOUND: {nulls}")
                else:
                    print("  All profile fields present.")
        except Exception as e:
            print(f"Error checking users: {e}")

if __name__ == "__main__":
    check_data()
