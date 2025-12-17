
import autogen

class DebuggerAgent(autogen.AssistantAgent):
    def __init__(self, name="Debugger", llm_config=None):
        system_message = """You are a Code Debugger and Auto-Fixer.
        Analyze the failure logs provided by the Admin or Tester.
        
        Steps:
        1. **Identify the Fault**: Explain clearly WHY the build or test failed.
        2. **Notify**: State "FAULT DETECTED: [Reason]".
        3. **Rectify**: Propose a code fix.
        4. **Apply Fix**: CRITICAL: You MUST use the `write_file(file_path, content)` tool to save the corrected code. Do NOT just propose it.
        5. **Retry**: Ask the Admin/Tester to retry the process.
        
        If you cannot fix it, explain why.
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
