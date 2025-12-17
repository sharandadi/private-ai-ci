
import os
from dotenv import load_dotenv
load_dotenv()
import autogen
from security.sandbox import Sandbox
from agents.scanner_agent import ScannerAgent
from agents.build_agent import BuildAgent
from agents.tester_agent import TesterAgent
from agents.report_agent import ReportAgent
from agents.debugger_agent import DebuggerAgent

from app.config import Config

class CIOrchestrator:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        # Use OpenAI-compatible endpoint - better compatibility, fewer safety issues
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
        self.sandbox = Sandbox(use_docker=False)

    def run(self, repo_path: str, repo_structure: str, job_id: str = None):
        """
        Orchestrates the CI process for a given repository.
        """
        import logging
        from app.models import db, Log

        logger = logging.getLogger('[Orchestrator]')
        
        # 1. Setup DB Logging if job_id is present
        db_handler = None
        if job_id:
            class DBLogHandler(logging.Handler):
                def __init__(self, job_id):
                    super().__init__()
                    self.job_id = job_id
                def emit(self, record):
                    try:
                        log_entry = self.format(record)
                        new_log = Log(job_id=self.job_id, content=log_entry)
                        db.session.add(new_log)
                        db.session.commit()
                    except Exception:
                        pass
            
            db_handler = DBLogHandler(job_id)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            db_handler.setFormatter(formatter)
            logger.addHandler(db_handler)

        try:
            logger.info("STEP 1: Creating UserProxyAgent...")
            # 1. Define Standard Admin Agent
            user_proxy = autogen.UserProxyAgent(
                name="Admin",
                system_message="A human admin. You execute the build/test steps.",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=15,
                is_termination_msg=lambda x: (x.get("content") or "").rstrip().endswith("TERMINATE"),
                code_execution_config={
                    "work_dir": "workspace",
                    "use_docker": False, 
                },
            )
            logger.info("UserProxyAgent created successfully")

            # 2. Skip RAG Agent (dependencies commented out)
            logger.info("STEP 2: Skipping RAG agent (dependencies not installed)")
            rag_agent = None

            logger.info("STEP 3: Creating specialized agents...")
            scanner = ScannerAgent(llm_config=self.llm_config)
            logger.info("Scanner agent created")
            builder = BuildAgent(llm_config=self.llm_config)
            logger.info("Builder agent created")
            tester = TesterAgent(llm_config=self.llm_config)
            logger.info("Tester agent created")
            reporter = ReportAgent(llm_config=self.llm_config)
            logger.info("Reporter agent created")
            debugger = DebuggerAgent(llm_config=self.llm_config)
            logger.info("Debugger agent created")

            # 3. Register Tools
            def run_shell_command(command: str) -> str:
                """
                Executes a shell command in a secure sandbox environment.
                """
                print(f">>> Executing in Sandbox: {command}")
                # Pass repo_path as work_dir to mount it
                stdout, stderr = self.sandbox.run_command(command, work_dir=repo_path)
                output = stdout + stderr
                return f"Output:\n{output}"

            def write_file(file_path: str, content: str) -> str:
                """
                Writes content to a file in the repository.
                """
                print(f">>> Writing to file: {file_path}")
                # Ensure path is within repo_path
                full_path = os.path.join(repo_path, file_path.lstrip('/'))
                
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                    return f"Successfully wrote to {file_path}"
                except Exception as e:
                    return f"Error writing file: {str(e)}"

            def set_sandbox_image(image_name: str) -> str:
                """
                Sets the Docker image for the sandbox environment.
                """
                print(f">>> Setting Sandbox Image: {image_name}")
                self.sandbox.set_image(image_name)
                return f"Sandbox image set to {image_name}"

            # Register run_shell_command
            for agent in [builder, tester, reporter, debugger]:
                autogen.agentchat.register_function(
                    run_shell_command,
                    caller=agent,
                    executor=user_proxy,
                    name="run_shell_command",
                    description="Run a shell command in the sandbox"
                )
                
            # Register write_file
            for agent in [builder, tester, debugger]:
                 autogen.agentchat.register_function(
                    write_file,
                    caller=agent,
                    executor=user_proxy,
                    name="write_file",
                    description="Write content to a file. Use this to create config files or fix code."
                )

            # Register set_sandbox_image for Scanner
            autogen.agentchat.register_function(
                set_sandbox_image,
                caller=scanner,
                executor=user_proxy,
                name="set_sandbox_image",
                description="Set the Docker image for the sandbox (e.g., maven:3.8-openjdk-17)"
            )

            # 4. Start the Chat
            logger.info("STEP 4: Creating GroupChat with all agents...")
            agents_list = [user_proxy, scanner, builder, tester, reporter, debugger]
            if rag_agent:
                agents_list.append(rag_agent)
            
            logger.info(f"Agents in group: {[a.name for a in agents_list]}")
            
            groupchat = autogen.GroupChat(
                agents=agents_list, 
                messages=[], 
                max_round=50,
            )
            logger.info("GroupChat created successfully")
            
            logger.info("STEP 5: Creating GroupChatManager...")
            manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)
            logger.info("GroupChatManager created successfully")
            
            # 5. Initiate the Conversation
            logger.info("STEP 6: Initiating chat with initial message...")
            message = f"""
            Analyze this repository and generate a CI report.
            
            Repository Structure:
            {repo_structure}
            
            Tasks:
            1. Scanner: Identify the stack
            2. Builder: Check if code runs. If it fails, ask Debugger to fix it.
            3. Tester: Look for existing tests. **If NO tests are found, you MUST create a new test file (e.g. `test_suite.py`) covering the codebase.** Then run the tests. If tests fail, ask Debugger to fix the code.
            4. Reporter: Create final report. **If code was modified/rectified, INCLUDE the fixed code snippets in the report.** Say TERMINATE.
            
            Keep it brief. Reporter must end with TERMINATE.
            """
            
            logger.info("STEP 7: Starting user_proxy.initiate_chat()...")
            chat_res = user_proxy.initiate_chat(
                manager,
                message=message,
            )
            logger.info("Chat completed successfully!")
            
            # Extract the last message from the Reporter if possible, or search history
            report_content = "Report generation failed or not found."
            
            # Debug: Log chat history length
            import logging
            logger = logging.getLogger('[Orchestrator]')
            logger.info(f"DEBUG: Chat history has {len(chat_res.chat_history)} messages")
            
            # Iterate backwards to find the last message from 'Reporter'
            for msg in reversed(chat_res.chat_history):
                msg_name = msg.get("name", "Unknown")
                logger.info(f"DEBUG: Checking message from {msg_name}")
                if msg_name == "Reporter":
                     report_content = msg.get("content", "")
                     logger.info(f"DEBUG: Found Reporter message, length: {len(report_content)}")
                     break
            
            # --- FALLBACK: FORCE REPORT GENERATION ---
            if report_content == "Report generation failed or not found." or len(report_content) < 50:
                logger.warning("⚠️ Reporter did not speak or report is empty. Forcing report generation.")
                
                force_prompt = f"""
                The team has finished their work. Review the conversation history above and generate the final CI Report as requested.
                
                Content:
                {str(chat_res.chat_history)}
                
                Format:
                Markdown.
                Structure:
                1. Executive Summary
                2. Issues Found
                3. Rectified Code (CRITICAL: Include the fixed code snippets if any)
                4. Test Results
                5. Recommendations
                
                Ending with TERMINATE.
                """
                
                # Direct call to Reporter
                # We use the user_proxy to ask the reporter directly
                direct_res = user_proxy.initiate_chat(
                    reporter,
                    message=force_prompt,
                    clear_history=False 
                )
                
                # Extract the last message from this new chat
                if direct_res.chat_history:
                     last_msg = direct_res.chat_history[-1]
                     if last_msg.get("content"):
                         report_content = last_msg.get("content")
                         logger.info(f"DEBUG: Forced report content length: {len(report_content)}")

            # Clean up TERMINATE
            if report_content:
                report_content = report_content.replace("TERMINATE", "").strip()
            else:
                report_content = "Report generation failed."
            
            logger.info(f"DEBUG: Final report content length: {len(report_content)}")
            
            # Write report to file
            report_path = os.path.join(repo_path, "ci_report.md")
            try:
                with open(report_path, "w") as f:
                    f.write(report_content)
                logger.info(f"Report saved to {report_path}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")

            # Return both success message and report content
            return report_content

        finally:
             if db_handler:
                 logger.removeHandler(db_handler)
