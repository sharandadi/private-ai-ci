
import os
import shutil
from agents.orchestrator import CIOrchestrator

# Setup a mock repo
MOCK_REPO_PATH = os.path.join(
    os.getenv("WORKSPACE_BASE", os.getcwd()), 
    "mock_repo"
)

def setup_mock_repo():
    if os.path.exists(MOCK_REPO_PATH):
        shutil.rmtree(MOCK_REPO_PATH)
    os.makedirs(MOCK_REPO_PATH)
    
    # NOTE: NOT creating pom.xml. The Build Agent should detect this and create it.


    # Create Java file with a BUG
    src_dir = os.path.join(MOCK_REPO_PATH, "src/main/java/com/example")
    os.makedirs(src_dir)
    with open(os.path.join(src_dir, "App.java"), "w") as f:
        f.write("""package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("Hello World" // Missing closing parenthesis and semicolon
    }
}""")

    print(f"Created mock Java repo at {MOCK_REPO_PATH} with a deliberate bug.")
    return MOCK_REPO_PATH

def run_test():
    repo_path = setup_mock_repo()
    
    orchestrator = CIOrchestrator()
    print("Starting CI Orchestrator...")
    
    repo_structure = """
    - src/
      - main/
        - java/
          - com/
            - example/
              - App.java
    """
    
    orchestrator.run(repo_path, repo_structure)
    print("CI Orchestrator finished.")

if __name__ == "__main__":
    run_test()
