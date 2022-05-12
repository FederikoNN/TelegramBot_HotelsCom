import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


@dp.message_handler(state='*')
async def uncorrect_msg(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        await message.answer(
            'Вы ввели некорректные данные, начните поиск заново /help')
        await state.finish()
    except Exception as e:
        logging.exception(e)
        await state.finish()
