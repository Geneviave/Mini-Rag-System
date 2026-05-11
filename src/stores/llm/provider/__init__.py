#TIP: Initialize package exports here.
#stores/llm/provider/init.py
#استخدمت open ai لان ال ollama بتدعمها فهقدر اشتغل openai w ollama
from openai import OpenAI
class BaseProvider:
    #deh fun bta5od password w 3nwan el server
    #lw el 3nwan OpenAI → "https://api.openai.com/", Ollama → "http://localhost:11434/v1"
    def __init__(self, api_key: str, api_base: str):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        # ديه بتبعت الرد ل llm  تستنى الرد منه
    def generate(self, prompt: str, model: str, temperature: float = 0.2, max_tokens: int = 1000, system_prompt="You are an AI assistant specialized in CV analysis and candidate matching."):
        response = self.client.chat.completions.create(
            model=model,
            # انا اللي ببعت ف ال role هي ال user  ال prompt هي السؤال
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        # هنا لو رجع اكتر من رد باخد اول واحد
        return response.choices[0].message.content
    # الاتنين نفس الكود فرق ال عنوان السيرفر اللي هبعته هيقول عايزة اشتغل بايه
class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, api_base: str):
        super().__init__(api_key=api_key, api_base=api_base)

class OllamaProvider(BaseProvider):
    def __init__(self, api_key: str, api_base: str):
        super().__init__(api_key=api_key, api_base=api_base)

class LLMProviderFactory:
    @staticmethod
    # ديه مسئولة بترجع الprovidor المظبوط لو بعت ollama هتجيب OllamaProvider
    def get_provider(provider_type: str, api_key: str, api_base: str) -> BaseProvider:
        providers = {"openai": OpenAIProvider, "ollama": OllamaProvider}
        provider_type = provider_type.lower()
        if provider_type not in providers:
            raise ValueError(f"Unknown provider: {provider_type}")
        return providers[provider_type](api_key=api_key, api_base=api_base)