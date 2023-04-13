import logging
from typing import Dict

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery

# Initialize bot and dispatcher
API_TOKEN = "5861953499:AAHOSNaGSk9m2tQp1Ozz_vmARxT9HPh2xD4"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Callback data
menu_cb = CallbackData("menu", "action")
back_cb = CallbackData("back", "main_menu")

# Menu items
menu_items: Dict[str, str] = {
    "program": "Программа 📚",
    "place": "Место 📍",
    "price": "Цена 💰",
    "question": "Задать вопрос 🤔",
    "myact": "Подать заявку 📝",
}

# Inline keyboard
inline_keyboard = InlineKeyboardMarkup(row_width=2)
for action, description in menu_items.items():
    button = InlineKeyboardButton(description, callback_data=menu_cb.new(action=action))
    inline_keyboard.add(button)

# Back button
back_button = InlineKeyboardMarkup().add(InlineKeyboardButton("Назад", callback_data=back_cb.new(main_menu="main")))

# Messages and button descriptions
WELCOME_MESSAGE = (
    "Привет! 😃 Я бот школы искусств и творчества CoolScool. "
    "Выберите один из пунктов меню, чтобы узнать больше"
)


PROGRAM_MESSAGE = "Программа CoolScool 📚: ..."
PLACE_MESSAGE = "Адрес CoolScool 📍: Koh Phangan 🌴🌊"
PRICE_MESSAGE = "Цены на занятия в CoolScool 💰: ..."
QUESTION_MESSAGE = "Если у вас есть вопросы, свяжитесь с нами по телефону 📞: ..."
MYACT_MESSAGE = "Подать заявку на обучение 📝: ..."

MYACT_MESSAGE = "Чтобы подать заявку на обучение, заполните форму на нашем сайте: ..."
DESCRIPTIONS = {
    "program": PROGRAM_MESSAGE,
    "place": PLACE_MESSAGE,
    "price": PRICE_MESSAGE,
    "question": QUESTION_MESSAGE,
    "myact": MYACT_MESSAGE,
}


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message):
    """
    Handle the /start and /help commands
    """
    # Отправляем приветственное сообщение и инлайн-клавиатуру
    await message.reply(WELCOME_MESSAGE, reply_markup=inline_keyboard)

@dp.callback_query_handler(menu_cb.filter())
async def process_callback_menu(callback_query: CallbackQuery, callback_data: dict):
    """
    Process menu callback
    """
    # Получаем выбранный пункт меню и соответствующее описание
    action = callback_data["action"]
    description = DESCRIPTIONS[action]
    
    # Редактируем сообщение с выбранным пунктом меню и добавляем кнопку "Назад"
    message = await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                          message_id=callback_query.message.message_id,
                                          text=description,
                                          reply_markup=back_button)
    
    # Отвечаем на callback query, чтобы она не оставалась висеть
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(back_cb.filter(main_menu="main"))
async def process_callback_back_to_main(callback_query: CallbackQuery):
    """
    Process back callback to main menu
    """
    # Редактируем сообщение на главное меню
    message = await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                          message_id=callback_query.message.message_id,
                                          text=WELCOME_MESSAGE,
                                          reply_markup=inline_keyboard)
    
    # Отвечаем на callback query, чтобы она не оставалась висеть
    await bot.answer_callback_query(callback_query.id)
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

