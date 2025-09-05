import os
import subprocess
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

APP_SCRIPT = "main.py"
CHECK_INTERVAL = 300  # 5 minutes
PING_INTERVAL = 200   # 200 seconds to prevent Render sleep
RENDER_URL = "https://deployx-hzd6.onrender.com"  # <-- Replace with your actual Render URL

process = None

def is_process_running(name):
    try:
        output = subprocess.check_output(["pgrep", "-f", name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def start_app():
    global process
    print(f"Starting {APP_SCRIPT}...")
    process = subprocess.Popen(["python3", APP_SCRIPT])

def monitor_app():
    while True:
        if not is_process_running(APP_SCRIPT):
            print(f"{APP_SCRIPT} is not running. Restarting...")
            start_app()
        else:
            print(f"{APP_SCRIPT} is running.")
        time.sleep(CHECK_INTERVAL)

def keep_alive():
    while True:
        try:
            print(f"Pinging {RENDER_URL} to keep alive...")
            requests.get(RENDER_URL, timeout=10)
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")
        time.sleep(PING_INTERVAL)

@app.route("/")
def status():
    running = is_process_running(APP_SCRIPT)
    return f"{APP_SCRIPT} is {'running ✅' if running else 'not running ❌'}."

if __name__ == "__main__":
    # Start monitor in background
    threading.Thread(target=monitor_app, daemon=True).start()

    # Start keep-alive pinger in background
    threading.Thread(target=keep_alive, daemon=True).start()

    # Start Flask app
    app.run(host="0.0.0.0", port=9683)
