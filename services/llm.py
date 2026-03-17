from openai import Openai
from config.settings import settings
class LLMService:
    def __init__(self):
        self.client= OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model='gpt-5.2'
    
    def generate_response():
        