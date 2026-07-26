"""
Головний файл асистента.

Що вже вміє:
- якщо надсилаєш посилання (Instagram/TikTok/будь-яке) — бот пропонує категорію
  (ШІ вгадує сам, можна виправити кнопкою) і зберігає в базу
- /links [категорія] — показати збережені посилання
- будь-який інший текст — відповідає ШІ (Gemini) як універсальний чат
- /start — привітання і коротка інструкція

Що буде додано наступними модулями:
- Шафа: обробка фото одягу, аналіз образів
- Трекер фільмів: періодичні питання, ШІ складає відгук
- Пошук закладів/готелів (Google Places)
"""

import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import init_db, get_session, Link
from ai import ask_gemini, suggest_category, CATEGORIES

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

URL_PATTERN = re.compile(r"https?://\S+")

# тимчасове сховище: url, що чекає підтвердження категорії, по user_id
pending_links: dict[int, str] = {}


def category_keyboard(selected: str | None = None) -> InlineKeyboardMarkup:
    buttons = []
    for cat in CATEGORIES:
        text = f"✅ {cat}" if cat == selected else cat
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"cat:{cat}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Я твій асистент 💛\n\n"
        "Поки що я вмію:\n"
        "— зберігати посилання по категоріях (просто кинь посилання)\n"
        "— відповідати на будь-які питання (просто напиши текст)\n"
        "— /links — показати збережені посилання\n\n"
        "Шафу і трекер фільмів додамо наступним кроком."
    )


@dp.message(Command("links"))
async def cmd_links(message: Message):
    parts = message.text.split(maxsplit=1)
    category_filter = parts[1] if len(parts) > 1 else None

    session = get_session()
    query = session.query(Link).filter(Link.user_id == message.from_user.id)
    if category_filter:
        query = query.filter(Link.category == category_filter)
    links = query.order_by(Link.created_at.desc()).limit(20).all()
    session.close()

    if not links:
        await message.answer("Поки що нічого не збережено в цій категорії.")
        return

    text = "\n\n".join(f"[{l.category}] {l.url}" for l in links)
    await message.answer(text)


@dp.message(F.text.regexp(URL_PATTERN.pattern))
async def handle_link(message: Message):
    url_match = URL_PATTERN.search(message.text)
    url = url_match.group(0)

    guessed = suggest_category(url)
    pending_links[message.from_user.id] = url

    await message.answer(
        f"Схоже, це підходить під категорію «{guessed}». Все вірно?",
        reply_markup=category_keyboard(guessed),
    )


@dp.callback_query(F.data.startswith("cat:"))
async def handle_category_choice(callback: CallbackQuery):
    category = callback.data.split(":", 1)[1]
    url = pending_links.pop(callback.from_user.id, None)

    if not url:
        await callback.answer("Це посилання вже оброблено.")
        return

    session = get_session()
    link = Link(user_id=callback.from_user.id, url=url, category=category)
    session.add(link)
    session.commit()
    session.close()

    await callback.message.edit_text(f"Збережено в «{category}» ✅\n{url}")
    await callback.answer()


@dp.message(F.text)
async def handle_generic_text(message: Message):
    reply = ask_gemini(message.text)
    await message.answer(reply)


async def main():
    init_db()
    print("Бот запущено. Очікую повідомлення...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
