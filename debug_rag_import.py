
try:
    from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
    print("SUCCESS: RetrieveUserProxyAgent imported")
except ImportError as e:
    print(f"FAILURE: RetrieveUserProxyAgent error: {e}")

try:
    import chromadb
    print("SUCCESS: chromadb imported")
    from chromadb.utils import embedding_functions
    print("SUCCESS: embedding_functions imported")
except ImportError as e:
    print(f"FAILURE: chromadb error: {e}")
