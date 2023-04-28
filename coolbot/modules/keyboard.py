from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict
from aiogram.utils.callback_data import CallbackData

# Menu items
menu_items: Dict[str, str] = {
    "program": "Программа 📚",
    "place": "Место 📍",
    "price": "Цена 💰",
    "question": "Задать вопрос 🤔",
    "myact": "Подать заявку 📝",
}
# Callback data
menu_cb = CallbackData("menu", "action")
back_cb = CallbackData("back", "main_menu")
myact_cb = CallbackData("myact", "action")



# Gender button
gender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
boy_button = KeyboardButton('Мальчик \U0001F466')
girl_button = KeyboardButton('Девочка \U0001F467')
gender_keyboard.add(boy_button, girl_button)


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
