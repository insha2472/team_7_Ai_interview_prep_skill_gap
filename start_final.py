import subprocess
import os
import sys
import time

def start():
    log_file = "final_log.txt"
    cwd = r"d:\repos\team_7_Ai_interview_prep_skill_gap"
    # USE 'venv' instead of '.venv'
    python_path = os.path.join(cwd, "venv", "Scripts", "python.exe")
    
    with open(log_file, "w") as f:
        f.write(f"Starting server at {time.ctime()}\n")
        f.write(f"Python path: {python_path}\n")
        
        try:
            # Start uvicorn background
            process = subprocess.Popen(
                [python_path, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=cwd,
                stdout=f,
                stderr=f,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            f.write(f"Process started with PID: {process.pid}\n")
            time.sleep(3)
            if process.poll() is not None:
                f.write(f"Process exited early with code: {process.returncode}\n")
            else:
                f.write("Process still running after 3 seconds.\n")
        except Exception as e:
            f.write(f"Startup error: {str(e)}\n")

if __name__ == "__main__":
    start()
