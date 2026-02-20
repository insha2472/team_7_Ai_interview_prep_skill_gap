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
        print("--- Checking Users Data ---")
        try:
            sql = text("SELECT id, name, email, earned_badges, daily_xp FROM users")
            rows = conn.execute(sql).fetchall()
            for row in rows:
                print(f"\nUser: {row[1]} ({row[2]})")
                print(f"  earned_badges: {repr(row[3])}")
                try:
                    badges = json.loads(row[3]) if row[3] else []
                    print(f"  Valid JSON? YES - {badges}")
                except Exception as je:
                    print(f"  Valid JSON? NO - {je}")
                
                print(f"  daily_xp: {repr(row[4])}")
                try:
                    dxp = json.loads(row[4]) if row[4] else {}
                    print(f"  Valid JSON? YES - {dxp}")
                except Exception as je:
                    print(f"  Valid JSON? NO - {je}")
        except Exception as e:
            print(f"Error checking users: {e}")

if __name__ == "__main__":
    check_data()
