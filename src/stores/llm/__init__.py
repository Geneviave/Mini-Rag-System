# stores/llm/__init__.py
from stores.llm.provider import LLMProviderFactory
from stores.llm.tempelate import TemplateManager

class LLMStore:
    def __init__(self, provider: str, api_key: str, api_base: str,
                 model: str, language: str = "en",
                 temperature: float = 0.2, max_tokens: int = 1000):
        self.provider = LLMProviderFactory.get_provider(provider, api_key, api_base)
        self.template_manager = TemplateManager(language=language)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def ask(self, template_name: str, **kwargs) -> str:
        prompt = self.template_manager.get(template_name, **kwargs)
        return self.provider.generate(prompt, self.model, self.temperature, self.max_tokens)