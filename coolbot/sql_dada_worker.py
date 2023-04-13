import sqlite3

# Создаем таблицу applications
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS applications
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              phone TEXT NOT NULL,
              location TEXT NOT NULL)''')
conn.commit()
conn.close()

...

@dp.message_handler(content_types=['contact'])
async def process_contact_message(message: types.Message):
    """
    Handle contact message
    """
    # Сохраняем данные о заявке в базу данных
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO applications (name, phone, location) VALUES (?, ?, ?)",
              (message.from_user.full_name, message.contact.phone_number, ''))
    conn.commit()
    conn.close()

    # Отправляем сообщение с благодарностью за отправку контакта
    await message.reply("Спасибо за отправ
