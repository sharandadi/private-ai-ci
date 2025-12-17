from agents.base_agent import BaseAgent

class ScannerAgent(BaseAgent):
    def __init__(self):
        super().__init__('templates/system_scanner.txt')

    def scan_repo(self, repo_file_structure):
        """
        Analyzes the file structure to identify the stack.
        """
        # mock result
        return self.query_llm(f"Identify the stack for: {repo_file_structure}")
