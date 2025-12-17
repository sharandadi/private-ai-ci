
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

class CIOrchestrator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
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
        self.sandbox = Sandbox()

    def run(self, repo_path: str, repo_structure: str):
        """
        Orchestrates the CI process for a given repository.
        """
        import logging
        logger = logging.getLogger('[Orchestrator]')
        
        logger.info("STEP 1: Creating UserProxyAgent...")
        # 1. Define Standard Admin Agent
        user_proxy = autogen.UserProxyAgent(
            name="Admin",
            system_message="A human admin. You execute the build/test steps.",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=15,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
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
            Matches: Sandbox.run_command(command, work_dir)
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
            # For simplicity, we assume file_path is relative or needs to be joined
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
        agents_list = [user_proxy, scanner, builder, tester, reporter, debugger]
        if rag_agent:
            agents_list.append(rag_agent)


        # 4. Create Group Chat with simplified transitions
        logger.info("STEP 4: Creating GroupChat with all agents...")
        agents_list = [user_proxy, scanner, builder, tester, reporter, debugger]
        if rag_agent:
            agents_list.append(rag_agent)
        
        logger.info(f"Agents in group: {[a.name for a in agents_list]}")
        
        # Simplified: Let autogen decide speaker order
        groupchat = autogen.GroupChat(
            agents=agents_list, 
            messages=[], 
            max_round=15,  # Reduced from 50 to force completion
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
        2. Builder: Check if code runs
        3. Tester: Look for and run any tests
        4. Reporter: Create final report and say TERMINATE
        
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
                 
        # Clean up TERMINATE
        report_content = report_content.replace("TERMINATE", "").strip()
        
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
