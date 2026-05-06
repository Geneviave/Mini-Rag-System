# TIP: Initialize package exports here.
# stores/llm/tempelate/locales/en/__init__.py
class EnglishPrompts:
    EXTRACT_SKILLS = """
Extract all technical and soft skills from the following CV. Return as a list.
CV: {cv_text}
Skills:
"""
    MATCH_CANDIDATE = """
Answer the question based on the CV context below.
If not found, say "Not found in the documents."
Context: {context}
Question: {question}
Answer:
"""
    SUMMARIZE_CV = """
Summarize this CV in 3-5 sentences focusing on experience and key skills.
CV: {cv_text}
Summary:
"""
    SYSTEM_PROMPT = "You are an HR assistant. Answer only from the provided CV documents."