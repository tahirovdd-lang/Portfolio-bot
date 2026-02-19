import os
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
BRAND_NAME = os.getenv("BRAND_NAME", "PORTFOLIO")
TG_USERNAME = os.getenv("TG_USERNAME", "@your_username")
PHONE = os.getenv("PHONE", "+998 (__) ___-__-__")
INSTAGRAM = os.getenv("INSTAGRAM", "@instagram")

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
    f"👋 Привет! Я <b>{BRAND_NAME}</b>.\n"
    "Делаю <b>Telegram-ботов</b> и <b>Telegram WebApp</b> под бизнес.\n\n"
    "Нажми <b>🚀 Открыть портфолио</b> — покажу кейсы и услуги."
)

SERVICES = (
    "✅ <b>Услуги</b>\n"
    "• Telegram-боты (продажи, заявки, меню, запись)\n"
    "• Telegram WebApp (каталоги, корзина, оплаты)\n"
    "• Интеграции: Instagram, Яндекс Карты, Click/Payme, CRM\n"
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
    "Сюда можно добавить отзывы текстом или ссылку на страницу отзывов.\n"
    "Если хочешь — сделаю блок отзывов прямо в WebApp."
)

CONTACTS = (
    "📩 <b>Контакты</b>\n"
    f"• Telegram: {TG_USERNAME}\n"
    f"• Телефон/WhatsApp: {PHONE}\n"
    f"• Instagram: {INSTAGRAM}"
)

class Lead(StatesGroup):
    name = State()
    contact = State()
    task = State()

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
    data = await state.get_data()
    await state.clear()

    task = (message.text or "").strip()
    user = message.from_user

    text = (
        "🆕 <b>Новая заявка</b>\n\n"
        f"👤 Имя: {data.get('name','—')}\n"
        f"📞 Контакт: {data.get('contact','—')}\n"
        f"🧩 Задача: {task}\n\n"
        f"👤 TG: @{user.username if user.username else '—'} | ID: <code>{user.id}</code>"
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer("✅ Заявка отправлена! Я свяжусь с тобой.", reply_markup=main_kb())

@dp.message()
async def fallback(message: Message):
    # чтобы не терять пользователей
    await message.answer("Выбери раздел в меню 👇", reply_markup=main_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
