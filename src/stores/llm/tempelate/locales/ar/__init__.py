# TIP: Initialize package exports here.
# stores/llm/tempelate/locales/ar/__init__.py
class ArabicPrompts:
    EXTRACT_SKILLS = """
استخرج جميع المهارات من السيرة الذاتية التالية. أعد النتيجة كقائمة.
السيرة الذاتية: {cv_text}
المهارات:
"""
    MATCH_CANDIDATE = """
أجب على السؤال بناءً على السياق أدناه.
إذا لم تجد الإجابة قل "غير موجود في الوثائق."
السياق: {context}
السؤال: {question}
الإجابة:
"""
    SUMMARIZE_CV = """
لخّص هذه السيرة الذاتية في 3-5 جمل.
السيرة الذاتية: {cv_text}
الملخص:
"""
    SYSTEM_PROMPT = "أنت مساعد موارد بشرية. أجب فقط من الوثائق المقدمة."