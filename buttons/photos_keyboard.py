from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

photos_keyboard = InlineKeyboardMarkup(row_width=1,
                                       inline_keyboard=[[InlineKeyboardButton(
                                           text="Да",
                                           callback_data='photos_yes')],
                                           [InlineKeyboardButton(
                                               text="Нет",
                                               callback_data='photos_no')
                                           ]
                                       ])
