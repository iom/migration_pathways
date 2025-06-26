# config.py - CrewAI Configuration Settings

import os
from dotenv import load_dotenv

load_dotenv()

class CrewAIConfig:
    """Configuration settings for CrewAI migration assistance"""
    
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
    
    # Embedding Settings
    AZURE_EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL")
    AZURE_OPENAI_ENDPOINT_EMBED = os.getenv("AZURE_OPENAI_ENDPOINT_EMBED")
    AZURE_OPENAI_API_KEY_EMBED = os.getenv("AZURE_OPENAI_API_KEY_EMBED")
    AZURE_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION_EMBED = os.getenv("AZURE_OPENAI_API_VERSION_EMBED")
    
    # CrewAI Execution Settings
    MAX_RPM = 15  # Requests per minute limit
    MAX_EXECUTION_TIME = 120  # Maximum seconds for crew execution
    VERBOSE_LOGGING = True
    MEMORY_ENABLED = True
    
    # Agent Configuration
    AGENT_TEMPERATURE = 0.1  # Low temperature for consistent responses
    MAX_ITERATIONS = 3  # Maximum iterations per agent
    
    # Tool Configuration
    VECTOR_SEARCH_K = 8  # Number of documents to retrieve
    VECTOR_SEARCH_THRESHOLD = 0.3  # Similarity threshold
    RISK_ASSESSMENT_ENABLED = True
    
    # Crew Complexity Settings
    SIMPLE_CREW_KEYWORDS_THRESHOLD = 2  # Threshold for using full vs simplified crew
    CONVERSATION_HISTORY_LIMIT = 5  # Number of previous messages to include in context
    SESSION_MEMORY_LIMIT = 20  # Maximum messages stored per user session
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_settings = [
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_API_KEY, 
            cls.AZURE_DEPLOYMENT_NAME,
            cls.AZURE_EMBEDDING_MODEL,
            cls.AZURE_OPENAI_ENDPOINT_EMBED,
            cls.AZURE_OPENAI_API_KEY_EMBED,
            cls.AZURE_EMBEDDING_DEPLOYMENT_NAME
        ]
        
        missing_settings = [setting for setting in required_settings if not setting]
        
        if missing_settings:
            raise ValueError(f"Missing required CrewAI configuration: {missing_settings}")
        
        return True
    
    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration dictionary"""
        return {
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "azure_deployment": cls.AZURE_DEPLOYMENT_NAME,
            "temperature": cls.AGENT_TEMPERATURE
        }
    
    @classmethod
    def get_embedding_config(cls):
        """Get embedding configuration dictionary"""
        return {
            "model": cls.AZURE_EMBEDDING_MODEL,
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT_EMBED,
            "api_key": cls.AZURE_OPENAI_API_KEY_EMBED,
            "openai_api_version": cls.AZURE_OPENAI_API_VERSION_EMBED,
            "deployment": cls.AZURE_EMBEDDING_DEPLOYMENT_NAME
        }