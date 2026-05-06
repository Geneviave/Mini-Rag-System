# TIP: Initialize package exports here.
# stores/llm/provider/__init__.py
from openai import OpenAI
class BaseProvider:
    def __init__(self, api_key: str, api_base: str):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
    def generate(self, prompt: str, model: str, temperature: float = 0.2, max_tokens: int = 1000):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
class OpenAIProvider(BaseProvider):
    pass
class OllamaProvider(BaseProvider):
    pass
class LLMProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, api_key: str, api_base: str) -> BaseProvider:
        providers = {"openai": OpenAIProvider, "ollama": OllamaProvider}
        if provider_type not in providers:
            raise ValueError(f"Unknown provider: {provider_type}")
        return providers[provider_type](api_key=api_key, api_base=api_base)