import os
from dotenv import load_dotenv

load_dotenv()


try:
    import boto3
    # Use the region where the container is running (passed via -e AWS_DEFAULT_REGION)
    region = os.getenv('AWS_DEFAULT_REGION', 'ap-south-1')
    ssm = boto3.client('ssm', region_name=region)
    print(f"DEBUG: Initialized SSM client in region: {region}")
except ImportError:
    ssm = None
    print("DEBUG: boto3 not found, SSM disabled")

def get_secret(key, default):
    """Try to fetch from env, then SSM, then default."""
    env_val = os.getenv(key)
    if env_val:
        return env_val
    
    if ssm and os.getenv('AWS_EXECUTION_ENV'): # Only try SSM if on AWS
        try:
            # Assuming parameter name matches key, e.g. /CodeLens/GEMINI_API_KEY
            param = ssm.get_parameter(Name=f"/CodeLens/{key}", WithDecryption=True)
            return param['Parameter']['Value']
        except Exception:
            pass
            
    return default

class Config:
    GITHUB_WEBHOOK_SECRET = get_secret('GITHUB_WEBHOOK_SECRET', 'your_webhook_secret_here')
    OPENAI_API_KEY = get_secret('OPENAI_API_KEY', '')
    GEMINI_API_KEY = get_secret('GEMINI_API_KEY', '')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
