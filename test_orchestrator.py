#!/usr/bin/env python3
"""
Test script to run the orchestrator directly and see where it hangs.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("ORCHESTRATOR TEST SCRIPT")
print("=" * 60)

print("\n1. Importing orchestrator...")
from agents.orchestrator import CIOrchestrator

print("2. Creating orchestrator instance...")
orchestrator = CIOrchestrator()
print(f"   API Key configured: {bool(orchestrator.api_key)}")
print(f"   Config list: {orchestrator.config_list}")

print("\n3. Creating test repository structure...")
repo_path = "/tmp/test-repo"
os.makedirs(repo_path, exist_ok=True)

# Create a simple test file
with open(f"{repo_path}/test.py", "w") as f:
    f.write("print('Hello World')\n")

repo_structure = """
test.py
"""

print(f"   Test repo created at: {repo_path}")
print(f"   Structure:\n{repo_structure}")

print("\n4. Running orchestrator...")
print("   This is where it might hang. Watch for STEP logs...")
print("-" * 60)

try:
    result = orchestrator.run(repo_path, repo_structure)
    print("-" * 60)
    print("\n5. Orchestrator completed!")
    print(f"   Result length: {len(result) if result else 0}")
    print(f"   Result preview: {result[:200] if result else 'None'}...")
except Exception as e:
    print("-" * 60)
    print(f"\n5. ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
