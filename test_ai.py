import sys
import os
# Add current dir to path
sys.path.append(os.getcwd())

from utils.ai_agent import ai_analyse_skill_gap

def test():
    resume = "I am a Senior React Developer with 5 years of experience in JavaScript, TypeScript, and Redux."
    jd = "We are looking for a React Developer who knows JavaScript, TypeScript, and AWS."
    
    print("Testing AI Skill Gap Analysis...")
    try:
        result = ai_analyse_skill_gap(resume, jd)
        print(f"SUCCESS! Result: {result}")
    except Exception as e:
        print(f"FAILURE! Error: {e}")

if __name__ == "__main__":
    test()
