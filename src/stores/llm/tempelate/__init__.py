#TIP: Initialize package exports here.
#stores/llm/tempelate/init.py

#هنا بحدد انجلش و لا عربي
#بختار انهيه prompt و املا ال placeholders
#و يرجع ال prompt النهائي اللي هيرح ل ال llm
from stores.llm.tempelate.locales.en import EnglishPrompts
from stores.llm.tempelate.locales.ar import ArabicPrompts

class TemplateManager:
    # ديه بتجيب اللغة و لو مكتبتش من نفسه هتكون انجلش  هيروح يجيب انيه template
    def init(self, language: str = "en"):
        self.language = language
        self._templates = {"en": EnglishPrompts, "ar": ArabicPrompts}

    def get(self, template_name: str, kwargs) -> str:
        template_class = self._templates.get(self.language, EnglishPrompts)
        template = getattr(template_class, template_name, None)#هنا هيدخل ال template و يختار عايز يجيب ايه من جوة بالظبط
        if template is None:
            raise ValueError(f"Template '{template_name}' not found")
        return template.format(kwargs) # هنا بملي الفاراغات اللي كانت موجودة في ال template