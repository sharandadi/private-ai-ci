import subprocess
import os

class Sandbox:
    """
    Wrapper for running commands in a secure container (e.g. gVisor or just isolated Docker).
    """
    def __init__(self, image="python:3.11-slim"):
        self.image = image

    def set_image(self, image):
        """Sets the docker image to use."""
        self.image = image


    def run_command(self, command, work_dir=None):
        """
        Runs a command inside a docker container.
        Args:
            command: Shell command to run
            work_dir: Host directory (or volume path) to mount as workspace
        """
        cmd = ["docker", "run", "--rm"]
        
        # Check if running in Docker-outside-of-Docker mode
        dood_mode = os.getenv("DOCKER_CONTAINER_MODE") == "true"
        shared_vol = os.getenv("SHARED_VOL_NAME")
        workspace_base = os.getenv("WORKSPACE_BASE", "/workspace_data")

        # Mount workspace
        if work_dir:
            if dood_mode and shared_vol and work_dir.startswith(workspace_base):
                # We are in a container, writing to a mounted volume.
                # The Host Docker Engine only knows the volume name, not the path inside our container.
                # So we mount the named volume to /workspace_mount in the sibling container.
                # And we set WORKDIR to the subdirectory.
                
                rel_path = os.path.relpath(work_dir, workspace_base)
                # WORKDIR inside the sibling container
                container_work_path = f"/workspace_mount/{rel_path}"
                
                cmd.extend(["-v", f"{shared_vol}:/workspace_mount", "-w", container_work_path])
            elif os.path.exists(work_dir):
                # Standard host mode
                cmd.extend(["-v", f"{os.path.abspath(work_dir)}:/workspace", "-w", "/workspace"])
            
        cmd.extend([
            self.image,
            "sh", "-c", command
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr
