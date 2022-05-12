import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from loader import dp, db


@dp.message_handler(CommandStart(), state='*')
async def start_comm(message: types.Message, state: FSMContext):
    try:
        # Берет имя юзера
        name = message.from_user.full_name

        # Записываем юзера в БД, в случае если его там нет
        if db.check_user(message.from_user.id) is None:
            db.add_user(message.from_user.id, name)
        await message.answer(f"Привет, {message.from_user.full_name}!\n\n"
                             f"Телеграм бот поможет тебе узнать:\n"
                             f"1. Топ самых дешёвых отелей в городе (команда "
                             f"/lowprice)\n"
                             f"2. Узнать топ самых дорогих отелей в городе ("
                             f"команда /highprice)\n"
                             f"3. Узнать топ отелей, наиболее подходящих по "
                             f"цене и расположению от центра (самые дешёвые и "
                             f"находятся ближе всего к центру) (команда "
                             f"/bestdeal)\n"
                             f"4. Узнать историю поиска отелей (команда "
                             f"/history)")

    except Exception as e:
        logging.exception(e)
        await state.finish()
