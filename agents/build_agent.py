
import autogen

class BuildAgent(autogen.AssistantAgent):
    def __init__(self, name="Build_Engineer", llm_config=None):
        system_message = """You are a DevOps Build Engineer.
        Based on the identified stack, propose a series of shell commands to BUILD the application.
        Your Process:
        1. **Check for Config**: Look for standard build files (pom.xml, package.json, requirements.txt, Dockerfile).
        2. **Scaffold if Missing**: If a required config is missing (e.g., you have Java files but no pom.xml), YOU MUST CREATE IT.
           - Use the `write_file(path, content)` tool to create a minimal, valid configuration file.
           - Example: Create a simple `pom.xml` for Java 17.
        3. **Build**: Execute the build commands (e.g., `mvn install`, `npm install`).
        
        You MUST call the `run_shell_command` function to execute the commands.
        Do NOT just list the commands. Execute them.
        If the build fails, try to fix it or report the failure.
        """
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
        )
