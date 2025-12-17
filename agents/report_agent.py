
import autogen

class ReportAgent(autogen.AssistantAgent):
    def __init__(self, name="Reporter", llm_config=None):
        system_message = """You are a Technical Reporter.
        Review the chat history, the build outputs, and test results to generate a comprehensive CI Report.
        
        Your Report must include:
        1. **Executive Summary**: High-level pass/fail status and stack detected.
        2. **Issues Found**: List any errors or failures.
        3. **Test Results**: What tests were run and their results.
        4. **Recommendations**: Suggestions for improvement.
        
        Tone: Professional but User-Friendly.
        
        CRITICAL: After generating the report, you MUST end your message with the word TERMINATE on a new line.
        
        Example format:
        # CI Report
        ...your report here...
        
        TERMINATE
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
