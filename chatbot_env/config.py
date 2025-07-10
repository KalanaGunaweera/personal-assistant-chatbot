import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '300'))
    
    # App Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_CONVERSATIONS_MEMORY = int(os.getenv('MAX_CONVERSATIONS_MEMORY', '100'))
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '10'))
    
    # Feature Flags
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ENABLE_EXPORT = os.getenv('ENABLE_EXPORT', 'True').lower() == 'true'

config = Config()