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

PERSONA = (
    "Ти особистий асистент користувачки. Спілкуйся з нею як жива людина, "
    "завжди на «ти», тепло і просто, без канцеляриту. "
    "Ніколи не згадуй, що ти штучний інтелект, модель чи бот, і не пиши фраз "
    "типу «як ШІ я не можу» чи «я лише мовна модель». "
    "Відповідай прямо і по суті, без зайвих застережень і формальностей. "
    "Можеш мати легкий характер і живі емоції в тексті, але не перегравай."
)

model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=PERSONA)

CATEGORIES = ["Одяг", "Фільми", "Прикраси", "Заклади", "Інше"]


def ask_gemini(question: str) -> str:
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"Ой, щось не так з підключенням: {e}"


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


WARDROBE_CATEGORIES = ["Верх", "Низ", "Взуття", "Аксесуари", "Інше"]


def analyze_wardrobe_photo(image_bytes: bytes) -> dict:
    """
    Дивиться на фото речі одягу і повертає:
    - description: короткий людський опис (для назви в базі)
    - category: одна з WARDROBE_CATEGORIES
    - color: основний колір
    - season: сезон (літо/зима/демісезон/будь-який)
    """
    prompt = (
        "На фото — річ одягу або аксесуар. Дай відповідь СТРОГО у такому форматі, "
        "по одній властивості на рядок, без зайвих слів:\n"
        "ОПИС: <коротко, 3-5 слів, наприклад 'чорний светр з високим горлом'>\n"
        f"КАТЕГОРІЯ: <одне з: {', '.join(WARDROBE_CATEGORIES)}>\n"
        "КОЛІР: <основний колір>\n"
        "СЕЗОН: <літо / зима / демісезон / будь-який>"
    )
    try:
        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        )
        text = response.text

        result = {"description": "річ одягу", "category": "Інше", "color": "", "season": ""}
        for line in text.splitlines():
            if line.upper().startswith("ОПИС:"):
                result["description"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("КАТЕГОРІЯ:"):
                cat = line.split(":", 1)[1].strip()
                result["category"] = cat if cat in WARDROBE_CATEGORIES else "Інше"
            elif line.upper().startswith("КОЛІР:"):
                result["color"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("СЕЗОН:"):
                result["season"] = line.split(":", 1)[1].strip()
        return result
    except Exception as e:
        return {"description": f"не вдалось розпізнати ({e})", "category": "Інше", "color": "", "season": ""}

    
