import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import CallbackQuery, MediaGroup
from buttons.photos_keyboard import photos_keyboard
from loader import dp, db

from botrequests.api_requests.hotel_photos import hotel_photos
from botrequests.api_requests.hotels_in_city import hotels_in_city
from botrequests.api_requests.hotels_list import hotels_list


@dp.message_handler(Command('lowprice'), state='*')
async def command_low_price(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        await state.finish()

        await message.answer(
            'Напишите город, в котором будет производиться поиск отелей')

        await state.update_data(
            command_datetime=message.date.strftime('%d-%m-%Y %H:%M'))
        await state.update_data(command='/lowprice')

        await state.set_state('input_city_low')
    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.message_handler(state='input_city_low')
async def input_city_func(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        city = message.text
        sort = 'PRICE'
        await message.answer('Ищем отели...')

        city_id = hotels_in_city(city)

        hotels = hotels_list(city_id, sort)

        number_of_hotels = len(hotels)

        if number_of_hotels > 0:
            await state.update_data(city_id=city_id)
            await state.update_data(hotels=hotels)
            await state.update_data(number_of_hotels=number_of_hotels)
            await message.answer(
                f'Введите количество отелей, которое необходимо вывести в '
                f'результате, '
                f'но не больше {number_of_hotels}')

            await state.set_state('input_hotels_amount_low')
        else:
            await message.answer(f'Найдено 0 отелей по заданным параметрам\n'
                                 f'/lowprice')
            await state.finish()
    except Exception:
        await message.answer(f'Некорретные данные для поиска\n'
                             f'Попробуйте еще раз /lowprice')
        await state.finish()


@dp.message_handler(regexp='\d+', state='input_hotels_amount_low')
async def input_hotels_amount_func(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        hotels_amount = int(message.text)
        data = await state.get_data()
        number_of_hotels = data.get('number_of_hotels')

        if (hotels_amount <= number_of_hotels) and (hotels_amount > 0):

            await state.update_data(hotels_amount=hotels_amount)
            await message.answer('Вывести фотографии для каждого отеля?',
                                 reply_markup=photos_keyboard)

            await state.set_state('input_photos_low')

        else:

            await message.answer('Некорректное количество отелей для поиска\n'
                                 'Попробуйте еще раз /lowprice')
            await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.callback_query_handler(state='input_photos_low')
async def show_low_price_hotels(call: CallbackQuery, state: FSMContext):
    try:
        logging.info(f'{call.from_user.id} {call.data}')

        await call.answer()

        temp_hotel_amount = 10
        # photos = call.data.split('_')[-1]

        if call.data == 'photos_yes':
            await call.message.answer(f'Введите количество фотографий, '
                                      f'которое будет выводиться с каждым '
                                      f'отелем, но не больше '
                                      f'{temp_hotel_amount}')

            await state.set_state('input_photo_amount_low')
        else:
            await call.message.answer('Ожидайте ответа...')

            hotel_description = ''
            counter = 0

            data = await state.get_data()
            hotels_amount = int(data.get('hotels_amount'))
            hotels = data.get('hotels')
            hotels_history = ''

            for hotel in hotels:
                if hotels_amount != counter:
                    try:
                        hotel_name = hotel['name']
                        hotel_address = hotel['address']['streetAddress']
                        hotel_distance = hotel['landmarks'][0]['distance']
                        hotel_price = hotel.get('ratePlan').get('price')[
                            'current']

                        hotel_description += "Название отеля: {name}\nАдрес " \
                                             "отеля: {address}\nРасстояние от " \
                                             "центра города: {distance} " \
                                             "\nЦена за сутки: {price} " \
                                             "\n\n".format(
                            name=hotel_name, address=hotel_address,
                            distance=hotel_distance, price=hotel_price)
                        counter += 1
                        hotels_history += hotel_name + '\n'

                    except Exception as e:
                        logging.exception(e)
                        continue
                else:
                    break

            await call.message.answer(hotel_description)

            command_datetime = data.get('command_datetime')
            command = data.get('command')

            db.add_history(call.from_user.id, command, command_datetime,
                           hotels_history)

            await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.message_handler(regexp='\d+', state='input_photo_amount_low')
async def show_low_price_hotels_with_photo(message: types.Message,
                                           state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        await message.answer('Формируем сообщения...')

        counter_hotel = 0

        data = await state.get_data()
        hotels_amount = int(data.get('hotels_amount'))
        photo_amount = int(message.text)
        hotels = data.get('hotels')
        hotels_history = ''

        for hotel in hotels:
            try:
                if counter_hotel != hotels_amount:
                    album = MediaGroup()
                    hotel_id = hotel['id']
                    hotel_name = hotel['name']
                    hotel_address = hotel['address']['streetAddress']
                    hotel_distance = hotel['landmarks'][0]['distance']
                    hotel_price = hotel.get('ratePlan').get('price')['current']
                    photos_mass = hotel_photos(hotel_id)['hotelImages']
                    counter_photo = 0

                    for photo in photos_mass:
                        if photo_amount != counter_photo and photos_mass.index(
                                photo) < 10:
                            counter_photo += 1
                            photo_link = photo['baseUrl']
                            new_photo_link = photo_link.replace('{size}', 'z')
                            if (photo_amount - counter_photo) == 0:
                                hotel_description = "Название отеля: {name}\n" \
                                                    "Адрес отеля: {address}\n" \
                                                    "Расстояние от центра " \
                                                    "города: {distance} \n" \
                                                    "Цена за сутки: {price} " \
                                                    "\n\n".format(
                                    name=hotel_name,
                                    address=hotel_address,
                                    distance=hotel_distance,
                                    price=hotel_price)

                                album.attach_photo(photo=new_photo_link,
                                                   caption=hotel_description)
                            else:
                                album.attach_photo(photo=new_photo_link)

                        else:
                            break
                    counter_hotel += 1
                    hotels_history += hotel_name + '\n'
                else:
                    break

                await message.answer_media_group(media=album)

            except Exception as e:
                logging.exception(e)
                continue

        command_datetime = data.get('command_datetime')
        command = data.get('command')

        db.add_history(message.from_user.id, command, command_datetime,
                       hotels_history)

        await message.answer('Поиск завершён')
        await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()
