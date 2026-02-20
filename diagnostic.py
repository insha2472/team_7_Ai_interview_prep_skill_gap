print("Diagnostic Start")
import os
print("OS imported")
from dotenv import load_dotenv
print("Dotenv imported")
load_dotenv()
print("Dotenv loaded")
import socket
print("Socket imported")

def check_port(host, port):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except Exception as e:
        print(f"Error connecting to {host}:{port} -> {e}")
        return False

host = "aws-1-us-east-1.pooler.supabase.com"
port = 6543
print(f"Checking connectivity to {host}:{port}...")
if check_port(host, port):
    print("SUCCESS: Connection to DB host possible.")
else:
    print("FAILURE: Cannot reach DB host.")
print("Diagnostic End")
