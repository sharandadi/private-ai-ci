
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

print("Verifying imports...")
try:
    from app.main import app
    print("SUCCESS: app.main imported")
except ImportError as e:
    print(f"FAILURE: app.main import failed: {e}")

try:
    from agents.orchestrator import CIOrchestrator
    print("SUCCESS: agents.orchestrator imported")
except ImportError as e:
    print(f"FAILURE: agents.orchestrator import failed: {e}")

try:
    from agents.scanner_agent import ScannerAgent
    print("SUCCESS: agents.scanner_agent imported")
except ImportError as e:
    print(f"FAILURE: agents.scanner_agent import failed: {e}")

try:
    from agents.build_agent import BuildAgent
    print("SUCCESS: agents.build_agent imported")
except ImportError as e:
    print(f"FAILURE: agents.build_agent import failed: {e}")

try:
    from agents.tester_agent import TesterAgent
    print("SUCCESS: agents.tester_agent imported")
except ImportError as e:
    print(f"FAILURE: agents.tester_agent import failed: {e}")
    
try:
    from agents.report_agent import ReportAgent
    print("SUCCESS: agents.report_agent imported")
except ImportError as e:
    print(f"FAILURE: agents.report_agent import failed: {e}")

try:
    from agents.debugger_agent import DebuggerAgent
    print("SUCCESS: agents.debugger_agent imported")
except ImportError as e:
    print(f"FAILURE: agents.debugger_agent import failed: {e}")

try:
    import chromadb
    print("SUCCESS: chromadb imported")
except ImportError as e:
    print(f"FAILURE: chromadb import failed: {e}")

try:
    from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
    print("SUCCESS: RetrieveUserProxyAgent imported")
except ImportError as e:
    print(f"FAILURE: RetrieveUserProxyAgent import failed: {e}")

try:
    import google.generativeai
    print("SUCCESS: google.generativeai imported")
except ImportError as e:
    print(f"FAILURE: google.generativeai import failed: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("SUCCESS: sentence_transformers imported")
except ImportError as e:
    print(f"FAILURE: sentence_transformers import failed: {e}")

print("Verification Complete.")
