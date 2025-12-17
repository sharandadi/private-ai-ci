import os
import shutil
import uuid
import logging
from git import Repo # Requires: pip install GitPython

logger = logging.getLogger(__name__)

SANDBOX_ROOT = "/tmp/ai-ci-sandbox"

def clone_repository(repo_url, commit_sha):
    """
    Clones the user's repository to a secure temporary directory.
    Checks out the specific commit SHA to ensure we test exactly what was pushed.
    """
    # Create a unique path for this job to prevent collisions
    job_uuid = str(uuid.uuid4())[:8]
    local_path = os.path.join(SANDBOX_ROOT, job_uuid)
    
    try:
        # Ensure the directory is clean
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
            
        logger.info(f"Utils: Cloning {repo_url} to {local_path}...")
        
        # Clone the repo
        # Note: In production, consider adding authentication (e.g., SSH keys or Tokens)
        # to the repo_url if the repo is private.
        repo = Repo.clone_from(repo_url, local_path)
        
        # Checkout specific commit
        repo.git.checkout(commit_sha)
        
        logger.info(f"Utils: Successfully checked out {commit_sha}")
        return local_path

    except Exception as e:
        logger.error(f"Utils: Git Clone failed: {e}")
        # Clean up if partial clone happened
        cleanup_repository(local_path)
        raise e

def cleanup_repository(local_path):
    """
    Securely removes the code after testing to save space and maintain privacy.
    """
    if local_path and os.path.exists(local_path):
        try:
            shutil.rmtree(local_path)
            logger.info(f"Utils: Cleaned up sandbox at {local_path}")
        except Exception as e:
            logger.error(f"Utils: Cleanup failed: {e}")