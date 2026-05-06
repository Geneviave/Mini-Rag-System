# TIP: Initialize package exports here.
# stores/llm/tempelate/__init__.py
from stores.llm.tempelate.locales.en import EnglishPrompts
from stores.llm.tempelate.locales.ar import ArabicPrompts

class TemplateManager:
    def __init__(self, language: str = "en"):
        self.language = language
        self._templates = {"en": EnglishPrompts, "ar": ArabicPrompts}

    def get(self, template_name: str, **kwargs) -> str:
        template_class = self._templates.get(self.language, EnglishPrompts)
        template = getattr(template_class, template_name, None)
        if template is None:
            raise ValueError(f"Template '{template_name}' not found")
        return template.format(**kwargs)