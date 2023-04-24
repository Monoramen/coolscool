 


# Обработчик, который вызывается при отправке пола ребенка
@dp.callback_query_handler(gender_cb.filter(), state=ApplicationForm.child_gender)
async def process_child_gender(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    # Получаем пол ребенка из callback_data
    child_gender = callback_data.get("gender")

    # Сохраняем пол ребенка в стейте
    await state.update_data(child_gender=child_gender)

    # Переводим бота в состояние для получения имени родителя
    await ApplicationForm.parent_name.set()

    # Отправляем сообщение для получения имени родителя
    await callback_query.message.answer("Введите ваше имя")


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
    await message.answer(message_text)

    # Завершаем состояние и сбрасываем стейт
    await state.finish()
