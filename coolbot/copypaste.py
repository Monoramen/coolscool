import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text


# создаем клавиатуру с двумя кнопками
gender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
boy_button = KeyboardButton('Мальчик \U0001F466')
girl_button = KeyboardButton('Девочка \U0001F467')
gender_keyboard.add(boy_button, girl_button)


# задаем уровень логирования
logging.basicConfig(level=logging.INFO)

ADMIN_CHAT_ID = 191531906
# задаем токен бота
BOT_TOKEN = '5861953499:AAHOSNaGSk9m2tQp1Ozz_vmARxT9HPh2xD4'

# создаем экземпляр бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# создаем класс состояний для FSM
class ApplicationForm(StatesGroup):
    child_name = State()  # состояние для имени ребенка
    child_gender = State()  # состояние для пола ребенка
    parent_name = State()  # состояние для имени родителя
    parent_phone = State()  # состояние для телефона родителя

# создаем функцию-обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    """
    # отправляем сообщение с приветствием и инструкцией по заполнению заявки
    instructions = "Добро пожаловать! Для подачи заявки, пожалуйста, введите следующую информацию о ребенке:\n\n"\
                   "1. Имя ребенка\n"\
                   "2. Пол ребенка (мальчик или девочка)\n"\
                   "3. Имя и фамилию родителя\n"\
                   "4. Телефон родителя\n\n"\
                   "Введите /cancel в любое время, чтобы отменить заполнение заявки."
    await bot.send_message(chat_id=message.chat.id, text=instructions)

    # переводим бота в состояние child_name для получения имени ребенка
    await ApplicationForm.child_name.set()






# создаем функцию-обработки полученного сообщения
@dp.message_handler(state=ApplicationForm.child_gender)
async def process_child_gender(message: types.Message, state: FSMContext):
    """
    Обработчик для получения пола ребенка
    """
    # сохраняем пол ребенка в состояние
    await state.update_data(child_gender=message.text)
    
    # переводим бота в состояние parent_name для получения имени родителя
    await ApplicationForm.parent_name.set()    
    await bot.send_message(chat_id=message.chat.id, text="Введите, пожалуйста, имя и фамилию родителя")




@dp.message_handler(state=ApplicationForm.parent_name)
async def process_parent_name(message: types.Message, state: FSMContext):
    """
    Обработчик для получения имени родителя
    """
    # сохраняем имя родителя в состояние
    await state.update_data(parent_name=message.text)
    # переводим бота в состояние parent_phone для получения телефона родителя
    await ApplicationForm.parent_phone.set()
    await bot.send_message(chat_id=message.chat.id, text="Введите, пожалуйста свой телефон или @username для связи в мессенджерах")


@dp.message_handler(state=ApplicationForm.parent_phone)
async def process_parent_phone(message: types.Message, state: FSMContext):
    """
    Обработчик для получения телефона родителя
    """
    # сохраняем телефон родителя в состояние
    await state.update_data(parent_phone=message.text)
    # получаем данные из состояния и формируем сообщение с заявкой
    user_data = await state.get_data()
    child_name = user_data.get("child_name")
    child_gender = user_data.get("child_gender")
    parent_name = user_data.get("parent_name")
    parent_phone = user_data.get("parent_phone")
    message_text = f"Заявка на запись ребенка:\n"\
                   f"Имя: {child_name}\n"\
                   f"Пол: {child_gender}\n"\
                   f"Имя родителя: {parent_name}\n"\
                   f"Контакт родителя или @username: {parent_phone}"

    # отправляем сообщение с заявкой и предлагаем пользователю отправить новую заявку или завершить работу с ботом
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start"), KeyboardButton(text="/cancel")]
        ],
        resize_keyboard=True,
    )
    await bot.send_message(chat_id=message.chat.id, text=message_text, reply_markup=reply_markup)

    # завершаем работу с FSM и переводим бота в состояние "start"
    await state.finish()


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel для отмены заполнения заявки
    """
    # отменяем текущее состояние
    await state.finish()
    # отправляем сообщение пользователю о том, что заявка отменена
    await bot.send_message(chat_id=message.chat.id, text="Заявка отменена. Для начала заполнения новой заявки введите /start")


@dp.message_handler(state=ApplicationForm.child_gender)
async def process_child_gender(message: types.Message, state: FSMContext):
    """
    Обработчик для получения пола ребенка
    """
    # проверяем, что пользователь ввел корректный пол ребенка
    if message.text.lower() not in ["мальчик", "девочка"]:
        await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, укажите пол ребенка (мальчик или девочка)")

        # сохраняем пол ребенка в состояние
        await state.update_data(child_gender=message.text)

        # переводим бота в состояние parent_name для получения имени родителя
        await ApplicationForm.parent_name.set()
        await bot.send_message(chat_id=message.chat.id, text="Укажите, пожалуйста, Ваше имя и фамилию")
    return

@dp.message_handler(state=ApplicationForm.parent_name)
async def process_parent_name(message: types.Message, state: FSMContext):
    """
    Обработчик для получения имени родителя
    """
    # сохраняем имя родителя в состояние
    await state.update_data(parent_name=message.text)
    # переводим бота в состояние parent_phone для получения номера телефона родителя
    await ApplicationForm.parent_phone.set()
    await bot.send_message(chat_id=message.chat.id, text="Укажите, пожалуйста, номер телефона для связи")

@dp.message_handler(state=ApplicationForm.parent_phone, content_types=types.ContentTypes.CONTACT)
async def process_parent_phone(message: types.Message, state: FSMContext):
    """
    Обработчик для получения номера телефона родителя
    """
    # сохраняем номер телефона родителя в состояние
    await state.update_data(parent_phone=message.contact.phone_number)
    # получаем данные из состояния
    async with state.proxy() as data:
        child_name = data['child_name']
        child_gender = data['child_gender']
        parent_name = data['parent_name']
        parent_phone = data['parent_phone']

    # отправляем данные заявки администратору
    await bot.send_message(chat_id = "@mposenddata", text=f"Новая заявка:\n\nИмя ребенка: {child_name}\nПол ребенка: {child_gender}\nИмя родителя: {parent_name}\nНомер телефона родителя: {parent_phone}")

    # отправляем сообщение пользователю о том, что заявка успешно отправлена
    await bot.send_message(chat_id=message.chat.id, text="Спасибо! Ваша заявка отправлена. Мы свяжемся с Вами в ближайшее время.")

@dp.message_handler(state='*')
async def process_all_other_messages(message: types.Message, state: FSMContext):
    """
    Обработчик для обработки всех остальных сообщений
    """
    # отправляем сообщение пользователю о том, что его сообщение не распознано
    await bot.send_message(chat_id=message.chat.id, text="Извините, я не понимаю Вас. Пожалуйста, воспользуйтесь командой /start для начала работы с ботом.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
