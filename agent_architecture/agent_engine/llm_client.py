import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        # Implicitly loads from GOOGLE_API_KEY if set, or we can use api_key arg
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
             print("Warning: GEMINI_API_KEY not found in environment.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    def call_chat(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini model and returns the text response.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "text/plain", 
                }
            )
            return response.text
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
