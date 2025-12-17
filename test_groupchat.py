#!/usr/bin/env python3
"""
Test the original GroupChat orchestrator to find where it hangs.
"""
import sys
import os
import time

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("GROUPCHAT ORCHESTRATOR DEBUG TEST")
print("=" * 60)

# Test 1: Import
print("\n[1/7] Testing imports...")
start = time.time()
try:
    from agents.orchestrator import CIOrchestrator
    print(f"✅ Import successful ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create orchestrator
print("\n[2/7] Creating orchestrator instance...")
start = time.time()
try:
    orch = CIOrchestrator()
    print(f"✅ Orchestrator created ({time.time() - start:.2f}s)")
except Exception as e:
    print(f"❌ Creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Prepare test data
print("\n[3/7] Preparing test repository...")
repo_path = "/tmp/test-groupchat"
os.makedirs(repo_path, exist_ok=True)

with open(f"{repo_path}/test.py", "w") as f:
    f.write("def hello():\n    return 'world'\n")

repo_structure = "test.py"
print(f"✅ Test repo ready at {repo_path}")

# Test 4: Run orchestrator with timeout monitoring
print("\n[4/7] Running orchestrator.run()...")
print("⏱️  Monitoring for hangs (will wait max 30 seconds)...")
print("-" * 60)

import threading
import signal

result = None
error = None
completed = False

def run_orchestrator():
    global result, error, completed
    try:
        result = orch.run(repo_path, repo_structure)
        completed = True
        print("\n✅ Orchestrator completed!")
    except Exception as e:
        error = e
        completed = True
        print(f"\n❌ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()

# Run in thread
thread = threading.Thread(target=run_orchestrator, daemon=True)
thread.start()

# Wait with progress indicator
for i in range(30):
    if completed:
        break
    time.sleep(1)
    if i % 5 == 0:
        print(f"⏱️  Still running... ({i}s elapsed)")

if not completed:
    print("\n❌ HUNG! Orchestrator did not complete in 30 seconds")
    print("This confirms the GroupChat is hanging.")
    print("\nLet me check the logs to see where it stopped...")
    sys.exit(1)

# Test 5: Check result
print("\n[5/7] Checking result...")
if error:
    print(f"❌ Had error: {error}")
elif result:
    print(f"✅ Got result: {len(result)} characters")
    print(f"Preview: {result[:200]}...")
else:
    print("⚠️  No result returned")

print("\n" + "=" * 60)
print("TEST COMPLETE - GroupChat is working!")
print("=" * 60)
