import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from loader import dp, db


@dp.message_handler(Command('history'), state='*')
async def command_low_price(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        # Запрос в БД на получение массива записей истории поиска
        user_history = db.get_history(message.from_user.id)

        if not user_history:
            await message.answer('У вас нет истории поиска')
        else:
            hotels_history_text = ''
            for elem in user_history:
                hotels_history_text += f"Команда: {elem[2]}\n" \
                                       f"Дата и время команды: {elem[3]}\n" \
                                       f"Отели: \n{elem[4]}\n\n"

            await message.answer(text=hotels_history_text)

        await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()
