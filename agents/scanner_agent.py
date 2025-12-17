
import autogen

class ScannerAgent(autogen.AssistantAgent):
    def __init__(self, name="Scanner", llm_config=None):
        system_message = """You are a senior software engineer. 
        Analyze the provided file structure and identify the technology stack, languages, and frameworks used.
        You have access to a RAG agent named 'CodebaseOracle'.
        TO use RAG (CodebaseOracle), send a message to it.
        HOWEVER, if the file structure provided in the initial message is sufficient, identify the stack IMMEDIATELY without querying.
        
        Example: "Stack: Python. Framework: Flask."
        
        Use the information to be precise.
        Be concise. Output the detected stack clearly.
        
        CRITICAL: YOU MUST FIRST SET THE ENVIRONMENT.
        Identify the Docker Image required for this stack.
        You MUST call the `set_sandbox_image(image_name)` tool as your FIRST action.
        
        Examples:
        - python:3.11
        - maven:3.8-openjdk-17
        - node:18
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
