"""
Обгортка над Gemini API.
Дві функції зараз:
- ask_gemini: універсальна відповідь на будь-яке питання
- suggest_category: ШІ сам пропонує категорію для посилання
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

CATEGORIES = ["Одяг", "Фільми", "Прикраси", "Заклади", "Інше"]


def ask_gemini(question: str) -> str:
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"Вибач, сталася помилка при звʼязку з ШІ: {e}"


def suggest_category(url: str) -> str:
    prompt = (
        f"Ось посилання: {url}\n"
        f"Обери ОДНУ найбільш підходящу категорію з цього списку: {', '.join(CATEGORIES)}.\n"
        f"Врахуй тип платформи та контекст, якщо можеш його визначити з самого URL.\n"
        f"Відповідай ЛИШЕ назвою категорії, без пояснень."
    )
    try:
        response = model.generate_content(prompt)
        guess = response.text.strip()
        return guess if guess in CATEGORIES else "Інше"
    except Exception:
        return "Інше"
