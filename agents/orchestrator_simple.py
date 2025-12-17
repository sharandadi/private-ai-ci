
import os
from dotenv import load_dotenv
load_dotenv()
import autogen
from security.sandbox import Sandbox

class CIOrchestrator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.config_list = [
            {
                'model': 'gemini-2.5-flash',
                'api_key': self.api_key,
                'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
            }
        ]
        self.llm_config = {
            "config_list": self.config_list,
            "temperature": 0,
        }
        self.sandbox = Sandbox()

    def run(self, repo_path: str, repo_structure: str):
        """
        Sequential AI-powered CI pipeline:
        1. Analyze code
        2. Generate tests
        3. Run tests
        4. Generate report
        """
        import logging
        logger = logging.getLogger('[Orchestrator]')
        
        logger.info("=" * 60)
        logger.info("STARTING AI-POWERED CI PIPELINE")
        logger.info("=" * 60)
        
        # Create assistant that will do all the work
        assistant = autogen.AssistantAgent(
            name="CI_Assistant",
            system_message="""You are an expert CI/CD assistant. Your job is to:
            1. Analyze the code structure
            2. Generate comprehensive unit tests for the code
            3. Run the tests
            4. Report the results
            
            For Python code:
            - Generate pytest tests
            - Test all functions and edge cases
            - Run: pytest -v
            
            Always provide clear, actionable feedback.""",
            llm_config=self.llm_config,
        )
        
        # Create user proxy that executes code
        user_proxy = autogen.UserProxyAgent(
            name="Executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": repo_path,
                "use_docker": False,
            },
        )
        
        # Initial message
        message = f"""
Analyze this repository and generate comprehensive tests:

Repository Structure:
{repo_structure}

Repository Path: {repo_path}

Tasks:
1. Read the code files (especially .py files)
2. Generate unit tests for all functions
3. Save tests to test_generated.py
4. Run: pytest -v test_generated.py
5. Report results

When done, end with TERMINATE.
"""
        
        logger.info("Starting AI conversation...")
        try:
            chat_result = user_proxy.initiate_chat(
                assistant,
                message=message,
            )
            
            logger.info("AI conversation completed")
            
            # Extract report from chat history
            report_lines = ["# AI-Generated CI Report\n\n"]
            report_lines.append("## Conversation Summary\n\n")
            
            for msg in chat_result.chat_history[-5:]:  # Last 5 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                name = msg.get("name", role)
                
                if content and not content.startswith("exitcode:"):
                    report_lines.append(f"### {name}\n")
                    report_lines.append(f"```\n{content}\n```\n\n")
            
            report_content = ''.join(report_lines)
            logger.info(f"Report generated: {len(report_content)} characters")
            
        except Exception as e:
            logger.error(f"Error during AI execution: {e}")
            report_content = f"# CI Report\n\n## Error\n\n```\n{str(e)}\n```\n"
        
        logger.info("=" * 60)
        logger.info("CI PIPELINE COMPLETE")
        logger.info("=" * 60)
        
        return report_content
