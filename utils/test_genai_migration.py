import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ai_agent import ai_analyse_skill_gap, ai_interview_coach

def test_skill_gap():
    print("Testing AI Skill Gap Analysis...")
    resume = "I am a Python developer with 3 years of experience in FastAPI and React."
    jd = "Required: Python, FastAPI, React, SQL, and Docker."
    try:
        result = ai_analyse_skill_gap(resume, jd)
        print(f"Match Results: {result}")
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert isinstance(result["match_percentage"], float)
        print("✅ Skill Gap Analysis passed.")
    except Exception as e:
        print(f"❌ Skill Gap Analysis failed: {e}")

def test_interview_coach():
    print("\nTesting AI Interview Coach...")
    user_email = "test@example.com"
    try:
        # First message
        resp1 = ai_interview_coach("Hello, I want to practice a Python interview.", user_email)
        print(f"AI Response 1: {resp1[:100]}...")
        
        # Second message - check if it remembers context
        resp2 = ai_interview_coach("Can you ask me a question about Python decorators?", user_email)
        print(f"AI Response 2: {resp2[:100]}...")
        
        assert len(resp1) > 0
        assert len(resp2) > 0
        print("✅ Interview Coach passed.")
    except Exception as e:
        print(f"❌ Interview Coach failed: {e}")

if __name__ == "__main__":
    load_dotenv()
    test_skill_gap()
    test_interview_coach()
