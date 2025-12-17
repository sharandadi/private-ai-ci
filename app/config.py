import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your_webhook_secret_here')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
