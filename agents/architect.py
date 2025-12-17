from agents.base_agent import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__('templates/system_tester.txt') # Using tester prompt as placeholder, or create a specific architect one

    def plan_build(self, stack_info):
        """
        Generates a build plan and test code based on the stack.
        """
        return self.query_llm(f"Create a build plan for: {stack_info}")
