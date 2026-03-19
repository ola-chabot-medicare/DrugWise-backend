"""
LLM service - calls OpenAI GPT to generate answer, given user question
and retrieve FDA context from ChromaDB
"""

from openai import OpenAI
from config.settings import settings
from utils.logger import logger


""" 1. Client and System prompt """
# Single shared OpenAI client instance
client = OpenAI(api_key = settings.OPENAI_API_KEY)

# System prompt - tells GPT to behave properly as a medical assistant
SYSTEM_PROMPT = """You are a helpful medical information assistant. 
IMPORTANT GUIDELINES:
- Provide accurate information based on the FDA drug data provided in the context
- Always include appropriate medical disclaimers
- If information is not in the provided context, supplement with your general medical knowledge but clearly indicate it is not from FDA data
- Never provide medical advice or diagnose conditions
- Reference FDA data sources when possible
- Be clear about drug information, side effects
- If uncertain about any information, recommend professional medical consultation

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide relevant details from the FDA data
- Include important warnings if applicable"""



""" 2. Main function signature and build the prompt """
def generate_answer(question: str, context: str, model: str = "gpt-4o-mini") -> str:
    user_prompt = f"""Based on the following FDA drug information, answer the question.
If the FDA context is insufficient, supplement with your general medical knowledge and clearly label it as such.

    FDA Context: {context}
    Question: {question}

    Answer:"""


    """ 3. Call OpenAI with try/except """
    try:
        response = client.chat.completions.create(
            model = model,
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],

            max_completion_tokens = 500     # max length of GPT response
        )

        # GPT can return multi answers, I take the first one [0]
        answer = response.choices[0].message.content.strip()

        # Log how many tokens were used - useful for monitoring API cost
        logger.info(f"LLM response | model = {model} | tokens = {response.usage.total_tokens}")
        return answer
        
    except Exception as e:
        # Any OpenAI error (rate limit, timeout, auth) - don't crash, return a safe message
        logger.error(f"OpenAI API call failed: {e}")
        return "Sorry, I was unable to generate answer. Please try again!"