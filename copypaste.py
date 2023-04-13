import logging
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

API_TOKEN = 'YOUR_API_TOKEN_HERE'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Define the start command handler
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Давайте начнем регистрацию вашего ребенка. Напишите имя ребенка:")
    # Set the next expected message to be the child's age
    await TestStates.waiting_for_age.set()

# Define a state for waiting for the child's age
class TestStates(types.State):
    waiting_for_age = types.State()

# Define the age message handler
@dp.message_handler(state=TestStates.waiting_for_age)
async def process_age(message: types.Message, state: types.ChatState):
    # Save the child's name in the state
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Спасибо! Теперь напишите возраст ребенка:")
    # Set the next expected message to be the child's gender
    await TestStates.waiting_for_gender.set()

# Define a state for waiting for the child's gender
class TestStates(types.State):
    waiting_for_gender = types.State()

# Define the gender message handler
@dp.message_handler(state=TestStates.waiting_for_gender)
async def process_gender(message: types.Message, state: types.ChatState):
    # Save the child's age in the state
    async with state.proxy() as data:
        data['age'] = message.text
    await message.reply("Отлично! Теперь напишите пол ребенка:")
    # Set the next expected message to be the child's contact information
    await TestStates.waiting_for_contact.set()

# Define a state for waiting for the child's contact information
class TestStates(types.State):
    waiting_for_contact = types.State()

# Define the contact message handler
@dp.message_handler(state=TestStates.waiting_for_contact)
async def process_contact(message: types.Message, state: types.ChatState):
    # Save the child's gender in the state
    async with state.proxy() as data:
        data['gender'] = message.text
    await message.reply("Отлично! Напишите контактный номер родителя:")
    # Set the next expected message to be the end of the dialog
    await TestStates.waiting_for_end.set()

# Define a state for waiting for the end of the dialog
class TestStates(types.State):
    waiting_for_end = types.State()

# Define the final message handler
@dp.message_handler(state=TestStates.waiting_for_end)
async def process_end(message: types.Message, state: types.ChatState):
    # Save the child's contact information in the state
    async with state.proxy() as data:
        data['contact'] = message.text
        # Retrieve all the data collected in the state
        name = data['name']
        age = data['age']
        gender = data['gender']
        contact = data['contact']
    await message.reply(f"Спасибо за регистрацию вашего ребенка. Вы указали следующую информацию:\n\n")
