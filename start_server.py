import subprocess
import os
import sys

# use absolute path to python
python_path = r"d:\repos\team_7_Ai_interview_prep_skill_gap\.venv\Scripts\python.exe"
main_path = r"d:\repos\team_7_Ai_interview_prep_skill_gap\main.py"

with open("server_log.txt", "w") as f:
    f.write("Starting server...\n")
    try:
        proc = subprocess.Popen([python_path, main_path], 
                                stdout=f, 
                                stderr=f, 
                                cwd=r"d:\repos\team_7_Ai_interview_prep_skill_gap")
        f.write(f"Server PID: {proc.pid}\n")
    except Exception as e:
        f.write(f"Exception: {str(e)}\n")
