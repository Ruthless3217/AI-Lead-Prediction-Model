import google.generativeai as genai
import os
from backend.llm.base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel('gemini-flash-lite-latest')
        print("✅ Gemini Provider Initialized (Primary: gemini-flash-lite-latest)")

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            # Map parameters
            # Gemini doesn't use standard openai params like max_tokens directly in generate_content the same way
            # but we can configure generation_config
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=kwargs.get('max_tokens', 256),
                temperature=kwargs.get('temperature', 0.7),
            )
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            # Simple text extraction
            return response.text
        except Exception as e:
            print(f"Gemini Generation Error: {e}")
            raise e
