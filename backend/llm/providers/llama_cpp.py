import os
from backend.llm.base import LLMProvider
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class LlamaCppProvider(LLMProvider):
    def __init__(self, model_path=None, n_ctx=2048, n_threads=None):
        if Llama is None:
            raise ImportError("llama-cpp-python is not installed. Please install it to use LlamaCppProvider.")
            
        self.model_path = model_path or os.getenv("MODEL_PATH", "/app/backend/models/llama-3.1-8b-instruct-q4_K_M.gguf")
        
        if not os.path.exists(self.model_path):
             print(f"⚠️ Model not found at {self.model_path}. LLM features will be disabled.")
             self.llm = None
             return

        # Explicitly control threads
        actual_threads = n_threads or max(1, os.cpu_count() - 4) # Reduce thread contention
        n_batch = 512 # Process in larger batches for prompt eval
        
        print(f"Loading Llama model from {self.model_path}...")
        print(f"DEBUG: Llama Init Params -> n_ctx={n_ctx}, n_threads={actual_threads}, n_batch={n_batch}")
        
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=actual_threads, 
                n_batch=n_batch,
                verbose=True # Enable internal llama logs to see eval times
            )
            print("✅ Llama model loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load Llama model: {e}")
            self.llm = None

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.llm:
            return "Error: Model not loaded."

        # Default params
        max_tokens = kwargs.get("max_tokens", 512)
        temperature = kwargs.get("temperature", 0.7)
        stop = kwargs.get("stop", ["User:", "\n\n"])

        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                echo=False
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            print(f"Generation Error: {e}")
            return f"Error generating response: {e}"
