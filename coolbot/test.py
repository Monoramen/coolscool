import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import User
from modules.keyboard import *
from modules.messages import *
import re

phone_pattern = r'^\+?[1-9]\d{1,14}$'
# Создаем объект хранилища состояний
fsm_storage = MemoryStorage()

# Initialize bot and dispatcher
API_TOKEN = "5861953499:AAHOSNaGSk9m2tQp1Ozz_vmARxT9HPh2xD4"
ADMIN_CHAT_ID = 191531906


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=fsm_storage)  

# создаем класс состояний для FSM опроса пользователяУ
class ApplicationForm(StatesGroup):
    child_name = State()  # состояние для имени ребенка
    child_gender = State()  # состояние для пола ребенка
    parent_contact = State()  # состояние для имени родителя


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
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,\
                                    message_id=callback_query.message.message_id,\
                                    text=MYACT_MESSAGE)
        # удаляем инлайн-клавиатуру
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=back_button)
    else:
        # Редактируем сообщение с выбранным пунктом меню и добавляем кнопку "Назад"
        # Отвечаем на callback query, чтобы она не оставалась висеть
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,\
                                message_id=callback_query.message.message_id,\
                                text=description,\
                                reply_markup=back_button
                                )


@dp.message_handler(lambda message: message.text.lower() in ['да', 'ок', 'угу'])
async def start_application_form(message: types.Message):
    """
    Обработчик для запуска анкеты
    """
    # Удаляем предыдущее сообщение с инлайн-клавиатурой
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    # Отправляем сообщение о начале заполнения анкеты
    await bot.send_message(chat_id=message.chat.id, text="Отлично, начнем заполнение анкеты!")
    # переводим бота в состояние child_name для получения имени ребенка
    await ApplicationForm.child_name.set()
    await message.answer("Укажите имя вашего чада", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel для отмены заполнения заявки
    """
    # Удаляем предыдущее сообщение с инлайн-клавиатурой
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    # отменяем текущее состояние
    await state.finish()
    # отправляем сообщение пользователю о том, что заявка отменена
    await bot.send_message(chat_id=message.chat.id, text="Заявка отменена.\
                            Для начала заполнения новой заявки введите /start")

# Обработчик, который вызывается при отправке имени ребенка
@dp.message_handler(state=ApplicationForm.child_name)
async def process_child_name(message: types.Message, state: FSMContext):
    # Сохраняем имя ребенка в стейте
    await state.update_data(child_name=message.text)
    await message.answer("Укажите пол ребенка ", reply_markup = gender_keyboard)
    # Переводим бота в состояние для получения пола ребенка
    await ApplicationForm.child_gender.set()

# создаем функцию-обработки полученного сообщения
@dp.message_handler(state=ApplicationForm.child_gender)
async def process_child_gender(message: types.Message, state: FSMContext):
    """
    Обработчик для получения пола ребенка
    """
    # сохраняем пол ребенка в состояние
    await state.update_data(child_gender=message.text)
    # переводим бота в состояние parent_name для получения имени родителя
    await message.answer(text='Введите Имя Фамилия', reply_markup=ReplyKeyboardRemove())
    await ApplicationForm.parent_contact.set()
    


# Обработчик, который вызывается при отправке телефона родителя
@dp.message_handler(state=ApplicationForm.parent_contact)
async def process_parent_contact(message: types.Message, state: FSMContext):
    # Извлекаем контакт родителя из сообщения
    contact_pattern = r"^([А-Яа-я]+)\s+([А-Яа-я]+)$"
    match = re.match(contact_pattern, message.text)
    user: User = message.from_user
    username = user.username
    
    if match:
        # Если контакт введен корректно, сохраняем его в стейт
        parent_name = f"{match.group(1)} {match.group(2)}"
        parent_contact = username

        await state.update_data(parent_name=parent_name, parent_contact=f'@{username}')
        await message.reply("Спасибо, мы получили ваши данные.")
            # Получаем данные из стейта
        data = await state.get_data()
        # Сбрасываем состояние
        await state.finish()
        # Формируем сообщение с полученными данными
        message_text = f"Вы указали следующие данные:\n" \
                       f"Имя ребенка: {data['child_name']}\n" \
                       f"Пол ребенка: {data['child_gender']}\n" \
                       f"Имя родителя: {data['parent_name']}\n" \
                       f"Контакт родителя: {data['parent_contact']}\
                       \nДля перехода в главное меню нажми /start"
        # Отправляем сообщение с полученными данными
        # отправляем данные заявки администратору
        await bot.send_message(chat_id = "@mposenddata",\
                               text=f"Новая заявка:\n\n\
                               Имя ребенка: {data['child_name']}\n\
                               Пол ребенка: {data['child_gender']}\n\
                               Имя родителя:{data['parent_name']}\n\
                               Контакт родителя: {data['parent_contact']}")
        # отправляем сообщение пользователю о том, что заявка успешно отправлена
        await bot.send_message(chat_id=message.chat.id,\
                                text=f"Спасибо! Ваша заявка отправлена.\nМы свяжемся с Вами в ближайшее время.\n {message_text}")
        # Завершаем состояние и сбрасываем стейт
        await state.finish()
    else:
        # Если контакт введен некорректно, сообщаем об ошибке
        await message.reply("Имя и фамилия родителя должны быть указаны через пробел.\nПожалуйста, попробуйте еще раз.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)