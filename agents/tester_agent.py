
import autogen

class TesterAgent(autogen.AssistantAgent):
    def __init__(self, name="Test_Engineer", llm_config=None):
        system_message = """You are a QA Test Engineer.
        After the build is successful, propose a series of shell commands to TEST the application.
        Focus ONLY on running tests (unit tests, integration tests, linting).
        
        You MUST call the `run_shell_command` function to execute the commands.
        Do NOT just list the commands. Execute them.
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
