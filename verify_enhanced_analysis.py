from utils.ai_agent import ai_analyse_skill_gap
import json

resume = "Experienced Python developer with 5 years in FastAPI, PostgreSQL, and AWS. Strong skills in software architecture and team leadership."
jd = "Looking for a Senior Backend Engineer proficient in Python, FastAPI, and Kubernetes. Experience with Redis and monitoring tools like Prometheus is a plus."

print("Running skill analysis...")
log_data = {"status": "starting", "results": None, "error": None}

try:
    result = ai_analyse_skill_gap(resume, jd)
    log_data["results"] = result
    log_data["status"] = "success"
    
except Exception as e:
    log_data["error"] = str(e)
    log_data["status"] = "error"

with open("verification_log.json", "w") as f:
    json.dump(log_data, f, indent=2)

print("Finished. Log written to verification_log.json")
