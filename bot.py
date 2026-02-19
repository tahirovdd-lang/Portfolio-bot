import os
import json
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

BRAND_NAME = os.getenv("BRAND_NAME", "TG Studio")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@Ecosystem_portfolio_bot")
PHONE = os.getenv("PHONE", "+998 (93) 746-00-22")
EMAIL = os.getenv("EMAIL", "tahirov.dd@gmail.com")
TG_CONTACT = os.getenv("TG_CONTACT", "@Yaki_Tahirov")

if not BOT_TOKEN or not ADMIN_ID or not WEBAPP_URL:
    raise SystemExit("❌ Заполни BOT_TOKEN, ADMIN_ID, WEBAPP_URL в .env")

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


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
    "Нажми <b>🚀 Открыть портфолио</b> — там кейсы и можно оставить заявку прямо в приложении.\n\n"
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
    "Могу добавить отзывы в WebApp (текст/скрин) и отдельную страницу.\n"
)

CONTACTS = (
    "📩 <b>Контакты</b>\n"
    f"• Telegram: {TG_CONTACT}\n"
    f"• Телефон/WhatsApp: {PHONE}\n"
    f"• Почта: {EMAIL}\n"
    f"• Портфолио (WebApp): {WEBAPP_URL}"
)


# ---------- Обычная заявка через чат ----------
class Lead(StatesGroup):
    name = State()
    contact = State()
    task = State()
    budget = State()
    deadline = State()


@dp.message(F.text.in_({"/start", "start"}))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_kb())


@dp.message(F.text == "🧩 Услуги")
async def services(message: Message):
    await message.answer(SERVICES, reply_markup=main_kb())


@dp.message(F.text == "💰 Прайс")
async def pricing(message: Message):
    await message.answer(PRICING, reply_markup=main_kb())


@dp.message(F.text == "⭐️ Отзывы")
async def reviews(message: Message):
    await message.answer(REVIEWS, reply_markup=main_kb())


@dp.message(F.text == "📩 Контакты")
async def contacts(message: Message):
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


# ---------- ✅ Заявка из WebApp (sendData) ----------
@dp.message(F.web_app_data)
async def webapp_lead(message: Message):
    """
    WebApp отправляет JSON через Telegram.WebApp.sendData()
    Aiogram получает в message.web_app_data.data
    """
    raw = message.web_app_data.data or ""
    user = message.from_user

    try:
        payload = json.loads(raw)
    except Exception:
        payload = {"text": raw}

    name = (payload.get("name") or "—").strip()
    contact = (payload.get("contact") or "—").strip()
    task = (payload.get("task") or "—").strip()
    budget = (payload.get("budget") or "—").strip()
    deadline = (payload.get("deadline") or "—").strip()
    source = (payload.get("source") or "webapp").strip()

    admin_text = (
        "🆕 <b>Новая заявка (из WebApp)</b>\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Контакт: {contact}\n"
        f"🧩 Задача: {task}\n"
        f"💰 Бюджет: {budget}\n"
        f"⏳ Срок: {deadline}\n"
        f"🔎 Source: {source}\n\n"
        f"👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>"
    )

    await bot.send_message(ADMIN_ID, admin_text)
    await message.answer("✅ Заявка отправлена из приложения! Я свяжусь с тобой.", reply_markup=main_kb())


@dp.message()
async def fallback(message: Message):
    await message.answer("Выбери раздел в меню 👇", reply_markup=main_kb())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
