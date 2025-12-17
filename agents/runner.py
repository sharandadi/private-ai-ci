from security.sandbox import Sandbox

class RunnerAgent:
    def __init__(self):
        self.sandbox = Sandbox()

    def execute_plan(self, build_plan):
        """
        Executes the build steps.
        """
        # Parse build plan and execute commands
        print(f"Executing plan: {build_plan}")
        # result = self.sandbox.run_command("echo 'Building...'")
        return "Build Success"
