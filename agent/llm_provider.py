from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass

# Gemini implementation using google-generativeai
import google.generativeai as genai

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use the current model name instead of gemini-pro
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def ask(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"LLM Error: {e}"