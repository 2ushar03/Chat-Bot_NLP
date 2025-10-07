from llama_cpp import Llama
class LlamaModelWrapper:
    def __init__(self, model_path: str):
        self.model = Llama(model_path=r'C:\Users\bbpat\.ollama\models\blobs\sha256-dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff')
    
    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.0) -> str:
        """
        Generate text from prompt. You may need to adapt arguments to your llama wrapper.
        """
        output = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
        if isinstance(output, dict) and "text" in output:
            return output["text"]
        elif isinstance(output, str):
            return output
        else:
            return str(output)
