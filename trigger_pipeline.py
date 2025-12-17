import requests
import hmac
import hashlib
import json
import subprocess
import os
import sqlite3

# Configuration
API_URL = "http://127.0.0.1:8080/webhook"
DB_PATH = "instance/ci.db"

def get_git_info():
    try:
        # Get current repo info
        repo_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        pusher = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        
        # Convert SSH url to HTTPS if needed for the backend to clone (optional, backend handles git clone usually)
        # But for the payload, we just send what we have.
        
        return {
            "ref": f"refs/heads/{branch}",
            "before": "0000000000000000000000000000000000000000",
            "after": commit_sha,
            "repository": {
                "clone_url": repo_url,
                "name": repo_url.split("/")[-1].replace(".git", ""),
                "full_name": "user/repo" # Dummy
            },
            "pusher": {
                "name": pusher,
                "email": "user@example.com"
            }
        }
    except Exception as e:
        print(f"Warning: Git extraction failed, using dummy data. Error: {e}")
        return {
            "ref": "refs/heads/main",
            "before": "0000000000000000000000000000000000000000",
            "after": "dummy_sha_123456",
            "repository": {
                "clone_url": "https://github.com/user/dummy-repo.git",
                "name": "dummy-repo",
                "full_name": "user/dummy-repo"
            },
            "pusher": {
                "name": "Test User",
                "email": "user@example.com"
            }
        }

def get_webhook_secret():
    try:
        # Connect to SQLite to get the secret
        # Note: App creates db in 'ci.db' in root or instance/ci.db depending on config.
        # Based on checking file list earlier, it seems to be 'ci.db' in root? 
        # Let's check both or assume root based on previous file listings.
        # Main.py said: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ci.db' -> relative to CWD.
        
        db_path = "app/instance/ci.db"
        if not os.path.exists(db_path):
             print(f"Database not found at {db_path}")
             return None
             
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT github_webhook_secret FROM settings LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return None
    except Exception as e:
        print(f"Error reading DB: {e}")
        return None

def trigger():
    print("🚀 Preparing to trigger local pipeline...")
    
    payload = get_git_info()
    if not payload:
        print("Failed to get git info. Are you in a git repo?")
        return

    secret = get_webhook_secret()
    if not secret:
        print("Failed to retrieve webhook secret from database.")
        print("Ensure the app has been started and setup is complete.")
        return

    payload_json = json.dumps(payload).encode()
    
    # Calculate Signature
    signature = hmac.new(secret.encode(), payload_json, hashlib.sha256).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Event": "push"
    }

    try:
        response = requests.post(API_URL, data=payload_json, headers=headers)
        print(f"📡 Request sent. Status: {response.status_code}")
        print(response.text)
        
        if response.status_code == 202:
            print("\n✅ Success! Job queued.")
            print("Check the dashboard: http://localhost:3000/dashboard")
        else:
            print("\n❌ Failed to trigger.")
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        print(f"Is the backend running on {API_URL}?")

if __name__ == "__main__":
    trigger()
