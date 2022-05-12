from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("help", "Помощь по командам бота"),
            types.BotCommand("lowprice", "Топ дешёвых отелей "),
            types.BotCommand("highprice", "Топ дорогих отелей"),
            types.BotCommand("bestdeal", "Топ отелей по цене и расположению"),
            types.BotCommand("history", "Узнать историю поиска"),
        ]
    )
