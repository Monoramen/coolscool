import logging
from typing import Dict
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re

phone_pattern = r'^\+?[1-9]\d{1,14}$'
# Создаем объект хранилища состояний
fsm_storage = MemoryStorage()

# Инициализируем объект диспетчера и связываем его с хранилищем состояний


# Initialize bot and dispatcher
API_TOKEN = "5861953499:AAHOSNaGSk9m2tQp1Ozz_vmARxT9HPh2xD4"
ADMIN_CHAT_ID = 191531906


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=fsm_storage)  


# Callback data
menu_cb = CallbackData("menu", "action")
back_cb = CallbackData("back", "main_menu")
myact_cb = CallbackData("myact", "action")

# создаем клавиатуру с двумя кнопками
gender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
boy_button = KeyboardButton('Мальчик \U0001F466')
girl_button = KeyboardButton('Девочка \U0001F467')
gender_keyboard.add(boy_button, girl_button)


# создаем класс состояний для FSM опроса пользователяУ
class ApplicationForm(StatesGroup):
    child_name = State()  # состояние для имени ребенка
    child_gender = State()  # состояние для пола ребенка
    parent_name = State()  # состояние для имени родителя
    parent_phone = State()  # состояние для телефона родителя


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

#Myact button
myact_keyboard = InlineKeyboardMarkup(row_width=2)
for action, description in menu_items.items():
    if action.startswith("myact"):
        button = InlineKeyboardButton(description, callback_data=myact_cb.new(action=action))
        myact_keyboard.add(button)




# Messages and button descriptions
WELCOME_MESSAGE = (
    "Привет! 😃 Я бот школы искусств и творчества CoolScool. "
    "Выберите один из пунктов меню, чтобы узнать больше:"
)
PROGRAM_MESSAGE = "Программа CoolScool 📚: \n 1. Математика\n 2. Керамика\n 3. Труды\n 4. Вышивание\n 5. Английский\n 6. Музыка\n 7. Паркур\n 8. Барабаны"
PLACE_MESSAGE = "Адрес CoolScool 📍: Koh Phangan 🌴🌊"
PRICE_MESSAGE = "Цены на занятия в CoolScool 💰: ..."
QUESTION_MESSAGE = "Если у вас есть вопросы, свяжитесь с нами по телефону 📞"
MYACT_MESSAGE = "Чтобы подать заявку на обучение, заполните форму для дальнейшей связи с нами."
DESCRIPTIONS = {
    "program": PROGRAM_MESSAGE,
    "place": PLACE_MESSAGE,
    "price": PRICE_MESSAGE,
    "question": QUESTION_MESSAGE,
    "myact": MYACT_MESSAGE,
}
myactstup = "Добро пожаловать! Для подачи заявки, пожалуйста, введите:\n\n"\
                   " Имя ребенка\n"\
                   "Введите /cancel в любое время, чтоб отменить заполнение заявки."

async def start_handler(message: types.Message, state: FSMContext):
    await state.set_state(ApplicationForm.child_name) # устанавливаем состояние для имени ребенка
    await message.answer("Введите имя ребенка")


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message):
    """
    Handle the /start and /help commands
    """
    # Отправляем приветственное сообщение и инлайн-клавиатуру
    await message.answer(WELCOME_MESSAGE, reply_markup=inline_keyboard)


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

@dp.callback_query_handler(menu_cb.filter())
async def process_callback_menu(callback_query: CallbackQuery, callback_data: dict):
    """
    Process menu callback
    """
    # Получаем выбранный пункт меню и соответствующее описание
    action = callback_data["action"]
    description = DESCRIPTIONS[action]

    if action == "myact":
        # переводим бота в состояние child_name для получения имени ребенка
        await ApplicationForm.child_name.set()
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Для того чтобы  начать заполнять анкету введите имя ребенка")

    else:

        # Редактируем сообщение с выбранным пунктом меню и добавляем кнопку "Назад"

    # Отвечаем на callback query, чтобы она не оставалась висеть
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,\
                                message_id=callback_query.message.message_id,\
                                text=description,\
                                reply_markup=back_button
                              )


# Обработчик, который вызывается при отправке имени ребенка
@dp.message_handler(state=ApplicationForm.child_name)
async def process_child_name(message: types.Message, state: FSMContext):
    # Сохраняем имя ребенка в стейте
    await state.update_data(child_name=message.text)

    # Переводим бота в состояние для получения пола ребенка
    await ApplicationForm.child_gender.set()

    # Отправляем сообщение для получения пола ребенка
    await message.answer("Укажите пол ребенка", reply_markup = gender_keyboard)



# создаем функцию-обработки полученного сообщения
@dp.message_handler(state=ApplicationForm.child_gender)
async def process_child_gender(message: types.Message, state: FSMContext):
    """
    Обработчик для получения пола ребенка
    """
    await message.answer(text='', reply_markup=types.ReplyKeyboardRemove())
    # сохраняем пол ребенка в состояние
    await state.update_data(child_gender=message.text)
    
    # переводим бота в состояние parent_name для получения имени родителя
    await ApplicationForm.parent_name.set()    
    
    await bot.send_message(chat_id=message.chat.id, text="Введите, пожалуйста, имя и фамилию родителя")



# Обработчик, который вызывается при отправке имени родителя
@dp.message_handler(state=ApplicationForm.parent_name)
async def process_parent_name(message: types.Message, state: FSMContext):
    # Сохраняем имя родителя в стейте
    await state.update_data(parent_name=message.text)

    # Переводим бота в состояние для получения телефона родителя
    await ApplicationForm.parent_phone.set()

    # Отправляем сообщение для получения телефона родителя
    await message.answer("Введите ваш телефон")


# Обработчик, который вызывается при отправке телефона родителя
@dp.message_handler(regexp=phone_pattern, state=ApplicationForm.parent_phone)
async def process_parent_phone(message: types.Message, state: FSMContext):
    # Сохраняем телефон родителя в стейте
    await state.update_data(parent_phone=message.text)

    # Получаем данные из стейта
    data = await state.get_data()

    # Формируем сообщение с полученными данными
    message_text = f"Вы указали следующие данные:\n" \
                   f"Имя ребенка: {data['child_name']}\n" \
                   f"Пол ребенка: {data['child_gender']}\n" \
                   f"Имя родителя: {data['parent_name']}\n" \
                   f"Телефон родителя: {data['parent_phone']}"

    # Отправляем сообщение с полученными данными
    # отправляем данные заявки администратору
    await bot.send_message(chat_id = "@mposenddata",\
                           text=f"Новая заявка:\n\n\
                           Имя ребенка: {data['child_name']}\n\
                           Пол ребенка: {data['child_gender']}\n\
                           Имя родителя:{data['parent_name']}\n\
                           Телефон родителя: {data['parent_phone']}")

    # отправляем сообщение пользователю о том, что заявка успешно отправлена
    await bot.send_message(chat_id=message.chat.id, text="Спасибо! Ваша заявка отправлена. Мы свяжемся с Вами в ближайшее время.")


    # Завершаем состояние и сбрасываем стейт
    await state.finish()




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

