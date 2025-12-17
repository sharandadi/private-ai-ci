
import autogen

class ReportAgent(autogen.AssistantAgent):
    def __init__(self, name="Reporter", llm_config=None):
        system_message = """You are a Technical Reporter.
        Review the chat history to generate a comprehensive CI Report.
        
        You MUST generate the markdown report content. Do NOT just say TERMINATE.
        
        Your Report must include:
        1. **Executive Summary**: High-level pass/fail status and stack detected.
        2. **Issues Found**: List any errors or failures.
        3. **Rectified Code**: CRITICAL. If any code was fixed or debugged, you MUST include the "diff" or the "full fixed code block" here.
        4. **Test Results**: detailed breakdown of the tests run. YOU MUST INCLUDE THE ACTUAL OUTPUT OF THE TEST COMMANDS (e.g. "Ran 3 tests in 0.005s... OK"). Do not just summarize.
        5. **Recommendations**: Suggestions for improvement.
        
        Tone: Professional but User-Friendly.
        
        Format:
        # CI Report
        [Detailed report content here]
        
        TERMINATE
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
