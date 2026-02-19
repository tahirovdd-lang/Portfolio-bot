import os
import json
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

logging.basicConfig(level=logging.INFO)

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "6013591658"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://tahirovdd-lang.github.io/Portfolio-bot/").strip()

BRAND_NAME = os.getenv("BRAND_NAME", "TG Studio — professional Telegram bot and WebApp solution").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "@Ecosystem_portfolio_bot").strip()
PHONE = os.getenv("PHONE", "+998 (93) 746-00-22").strip()
EMAIL = os.getenv("EMAIL", "tahirov.dd@gmail.com").strip()
TG_CONTACT = os.getenv("TG_CONTACT", "@Yaki_Tahirov").strip()

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN пустой. Заполни BOT_TOKEN в .env")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# ======================
# UI
# ======================
def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Открыть портфолио", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="🧩 Услуги"), KeyboardButton(text="💰 Прайс")],
            [KeyboardButton(text="⭐️ Отзывы"), KeyboardButton(text="📩 Контакты")],
            [KeyboardButton(text="📝 Оставить заявку")],
        ],
        resize_keyboard=True
    )


WELCOME = (
    f"👋 Привет! Это <b>{BRAND_NAME}</b>\n\n"
    "Я делаю <b>Telegram-ботов</b> и <b>Telegram WebApp</b> под бизнес.\n"
    "Нажми <b>🚀 Открыть портфолио</b> — там дизайн в стиле Sebtech + можно отправить запрос прямо из приложения.\n\n"
    f"🤖 Бот: <b>{BOT_USERNAME}</b>"
)

SERVICES = (
    "✅ <b>Услуги</b>\n"
    "• Telegram-боты: заявки, продажи, меню, запись, поддержка\n"
    "• Telegram WebApp: каталог, корзина, оплаты, мультиязык\n"
    "• Интеграции: Click/Payme, Instagram, Яндекс Карты, CRM\n"
    "• Дизайн и адаптация под iPhone/Android"
)

PRICING = (
    "💰 <b>Прайс (ориентир)</b>\n"
    "• Бот-визитка/портфолио: от 500 000 сум\n"
    "• Бот с заявками/формами: от 800 000 сум\n"
    "• WebApp-каталог: от 1 500 000 сум\n"
    "• WebApp с корзиной/оплатой: от 2 500 000 сум\n\n"
    "Точная стоимость зависит от задач — оставь заявку."
)

REVIEWS = (
    "⭐️ <b>Отзывы</b>\n"
    "Добавлю отзывы в WebApp (текст/скрины) и отдельную страницу.\n"
)

CONTACTS = (
    "📩 <b>Контакты</b>\n"
    f"• Telegram: {TG_CONTACT}\n"
    f"• Телефон/WhatsApp: {PHONE}\n"
    f"• Почта: {EMAIL}\n"
    f"• Портфолио (WebApp): {WEBAPP_URL}"
)


# ======================
# CHAT LEAD FORM (FSM)
# ======================
class Lead(StatesGroup):
    name = State()
    contact = State()
    task = State()
    budget = State()
    deadline = State()


# ✅ ВАЖНО: CommandStart() гарантированно ловит /start и /start@bot
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_kb())


@dp.message(F.text == "🧩 Услуги")
async def services_cmd(message: Message):
    await message.answer(SERVICES, reply_markup=main_kb())


@dp.message(F.text == "💰 Прайс")
async def pricing_cmd(message: Message):
    await message.answer(PRICING, reply_markup=main_kb())


@dp.message(F.text == "⭐️ Отзывы")
async def reviews_cmd(message: Message):
    await message.answer(REVIEWS, reply_markup=main_kb())


@dp.message(F.text == "📩 Контакты")
async def contacts_cmd(message: Message):
    await message.answer(CONTACTS, reply_markup=main_kb())


@dp.message(F.text == "📝 Оставить заявку")
async def lead_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Lead.name)
    await message.answer("📝 Как тебя зовут?")


@dp.message(Lead.name)
async def lead_name(message: Message, state: FSMContext):
    await state.update_data(name=(message.text or "").strip())
    await state.set_state(Lead.contact)
    await message.answer("Оставь контакт (телефон или @username):")


@dp.message(Lead.contact)
async def lead_contact(message: Message, state: FSMContext):
    await state.update_data(contact=(message.text or "").strip())
    await state.set_state(Lead.task)
    await message.answer("Кратко: что нужно сделать? (бот / WebApp / сайт / интеграции)")


@dp.message(Lead.task)
async def lead_task(message: Message, state: FSMContext):
    await state.update_data(task=(message.text or "").strip())
    await state.set_state(Lead.budget)
    await message.answer("Какой бюджет примерно? (можно диапазон или “не знаю”)")


@dp.message(Lead.budget)
async def lead_budget(message: Message, state: FSMContext):
    await state.update_data(budget=(message.text or "").strip())
    await state.set_state(Lead.deadline)
    await message.answer("Сроки? (когда нужно запустить)")


@dp.message(Lead.deadline)
async def lead_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    deadline = (message.text or "").strip()
    user = message.from_user

    admin_text = (
        "🆕 <b>Новая заявка (из чата)</b>\n\n"
        f"👤 Имя: {data.get('name','—')}\n"
        f"📞 Контакт: {data.get('contact','—')}\n"
        f"🧩 Задача: {data.get('task','—')}\n"
        f"💰 Бюджет: {data.get('budget','—')}\n"
        f"⏳ Срок: {deadline}\n\n"
        f"👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>"
    )

    await bot.send_message(ADMIN_ID, admin_text)
    await message.answer("✅ Заявка отправлена! Я свяжусь с тобой.", reply_markup=main_kb())


# ======================
# WEBAPP sendData HANDLER
# ======================
@dp.message(F.web_app_data)
async def webapp_data_handler(message: Message):
    raw = message.web_app_data.data or ""
    user = message.from_user

    try:
        payload = json.loads(raw)
    except Exception:
        payload = {"source": "unknown", "text": raw}

    src = (payload.get("source") or "webapp").strip()

    # Консультация из WebApp
    if src in ("consult", "lead", "form"):
        name = (payload.get("name") or "—").strip()
        contact = (payload.get("contact") or "—").strip()
        task = (payload.get("task") or "—").strip()
        budget = (payload.get("budget") or "—").strip()
        deadline = (payload.get("deadline") or "—").strip()

        admin_text = (
            "🆕 <b>Консультация (WebApp)</b>\n\n"
            f"👤 Имя: {name}\n"
            f"📞 Контакт: {contact}\n"
            f"🧩 Задача: {task}\n"
            f"💰 Бюджет: {budget}\n"
            f"⏳ Срок: {deadline}\n\n"
            f"👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>"
        )
        await bot.send_message(ADMIN_ID, admin_text)
        await message.answer("✅ Заявка отправлена из приложения! Я свяжусь с вами.", reply_markup=main_kb())
        return

    # Корзина / запрос
    if src == "cart":
        items = payload.get("items") or []
        total = payload.get("total") or 0

        lines = []
        for it in items[:50]:
            title = it.get("title") or it.get("name") or "—"
            qty = it.get("qty", 0)
            price = it.get("price", 0)
            cat = it.get("cat", "")
            sub = it.get("sub", "")
            extra = f" ({cat}/{sub})" if (cat or sub) else ""

            if price:
                lines.append(f"• {title}{extra} — {qty} × {int(price):,}".replace(",", " "))
            else:
                lines.append(f"• {title}{extra} — {qty}")

        admin_text = (
            "🛒 <b>Запрос из корзины (WebApp)</b>\n\n"
            + ("\n".join(lines) if lines else "—")
            + f"\n\n<b>Итого:</b> {int(total):,} сум".replace(",", " ")
            + f"\n\n👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>"
        )

        await bot.send_message(ADMIN_ID, admin_text)
        await message.answer("✅ Запрос отправлен! Я свяжусь с вами.", reply_markup=main_kb())
        return

    # fallback
    await bot.send_message(
        ADMIN_ID,
        "📩 <b>WebApp Data (unknown)</b>\n"
        f"👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>\n"
        f"<pre>{raw}</pre>"
    )
    await message.answer("✅ Данные получены.", reply_markup=main_kb())


@dp.message()
async def fallback(message: Message):
    await message.answer("Выбери раздел в меню 👇", reply_markup=main_kb())


# ======================
# RUN
# ======================
async def main():
    logging.info("✅ Bot started polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
