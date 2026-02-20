from utils.ai_agent import ai_analyse_skill_gap
import json

resume = "Experienced Python developer with 5 years in FastAPI, PostgreSQL, and AWS. Strong skills in software architecture and team leadership."
jd = "Looking for a Senior Backend Engineer proficient in Python, FastAPI, and Kubernetes. Experience with Redis and monitoring tools like Prometheus is a plus."

print("Running skill analysis...")
try:
    result = ai_analyse_skill_gap(resume, jd)
    print("\nAnalysis Result:")
    print(json.dumps(result, indent=2))
    
    # Check for expected keys
    expected = ["matched_skills", "missing_skills", "priority_skills", "match_percentage"]
    missing = [k for k in expected if k not in result]
    if not missing:
        print("\nSUCCESS: All expected fields are present.")
    else:
        print(f"\nFAILURE: Missing fields: {missing}")
        
except Exception as e:
    print(f"\nERROR: {e}")
