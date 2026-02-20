import sys
import os
import json

# Add current dir to path
sys.path.append(os.getcwd())

from utils.ai_agent import ai_analyse_skill_gap

def test():
    # More realistic sample
    resume = """
    John Doe
    Experience: 3 years as a Frontend Developer.
    Skills: React, JavaScript, HTML, CSS, Git, Node.js, TypeScript.
    """
    jd = """
    We need a React Developer with experience in TypeScript, AWS, and Tailwind CSS.
    """
    
    print("--- STARTING AI TEST ---")
    try:
        result = ai_analyse_skill_gap(resume, jd)
        print("RESULT FROM AI AGENT:")
        print(json.dumps(result, indent=2))
        
        if not result.get("matched_skills") and not result.get("missing_skills"):
            print("WARNING: Both skill lists are empty!")
        if result.get("match_percentage") == 0.0:
            print("WARNING: Match percentage is 0.0!")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    print("--- TEST FINISHED ---")

if __name__ == "__main__":
    test()
