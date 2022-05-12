import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, MediaGroup

from buttons.photos_keyboard import photos_keyboard
from loader import dp, db

from botrequests.api_requests.hotel_photos import hotel_photos
from botrequests.api_requests.hotels_in_city import hotels_in_city
from botrequests.api_requests.hotels_list import hotels_list_price_distance


# Заходим по команде /bestdeal, и состояние указываем из любого - '*'
@dp.message_handler(Command('bestdeal'), state='*')
async def command_low_price(message: types.Message, state: FSMContext):
    try:
        # Записываем действия пользователя в лог файл, пишем его id и
        # команду, которую он ввел
        logging.info(f'{message.from_user.id} {message.text}')
        # Сбрасываем состояние, это необходимо сделать, чтобы пользователь
        # смог зайти в команду из любого состояния
        # иначе ответа не будет совсем и он останется в том же состоянии их
        # которого пытался перейти
        await state.finish()

        await message.answer(
            'Напишите город, в котором будет производиться поиск отелей')

        # Сохраняем данные через машину состояний
        await state.update_data(
            command_datetime=message.date.strftime('%d-%m-%Y %H:%M'))
        await state.update_data(command='/bestdeal')
        # Устанавливаем состояние
        await state.set_state('input_city_bestdeal')
    except Exception as e:
        # При возникноверии исключения, записываем его в лог файл с пометкой
        # исключение
        logging.exception(e)
        await state.finish()


@dp.message_handler(state='input_city_bestdeal')
async def price_range(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        await message.answer(
            'Введите диапазон цен в рублях, в формате: 700-2000')

        city = message.text
        await state.update_data(city=city)

        await state.set_state('send_price_range')
    except Exception as e:
        logging.exception(e)
        await state.finish()


# Регулярым выражением ограничиваем входные данные, а именно 'любое
# число-любое число'
@dp.message_handler(regexp='^\d+-\d+$', state='send_price_range')
async def distance_range(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        # Берем из входных данных начальную цену и конечную
        start_price = message.text.split('-')[0]
        finish_price = message.text.split('-')[-1]

        await state.update_data(start_price=start_price)
        await state.update_data(finish_price=finish_price)

        await message.answer(
            'Введите диапазон расстояния, на котором находится отель от '
            'центра в км, в формате: 1-5')

        await state.set_state('send_distance_range')
    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.message_handler(regexp='^\d+-\d+$', state='send_distance_range')
async def input_city_func(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        start_dist = float(message.text.split('-')[0])
        finish_dist = float(message.text.split('-')[-1])

        # Получаем данные из машины состояния
        data = await state.get_data()
        city = data.get('city')
        start_price = data.get('start_price')
        finish_price = data.get('finish_price')

        await message.answer('Ищем отели...')
        # Запрос через АПИ на получение id города по названию
        city_id = hotels_in_city(city)
        # Запрос через АПИ на получение отелей по id города с параметрами
        hotels = hotels_list_price_distance(city_id, start_price, finish_price)
        # Получаем количество отелей
        number_of_hotels = len(hotels)
        valid_hotels_counter = 0
        # Если найден хоть один отель
        if number_of_hotels > 0:
            sorted_hotels = []
            for hotel in hotels:
                # Берем данные по расстоянию от центра города до отеля в
                # цифре, входные данные типа: 3,4 км
                hotel_ditance = float(
                    hotel['landmarks'][0]['distance'].split(' ')[0].replace(',',
                                                                            '.'))
                # Если расстояние от отеля до центра города попадает под
                # заданные от пользователя
                if (hotel_ditance >= start_dist) and (
                        hotel_ditance <= finish_dist):
                    sorted_hotels.append(hotel)
                    valid_hotels_counter += 1
            # Если нашли хоть один отель после сортировки по заданным
            # параметрам, то заносит данные в машину состояния
            # и идем дальше собирать информацию
            if valid_hotels_counter > 0:
                await state.update_data(city_id=city_id)
                await state.update_data(hotels=sorted_hotels)
                await state.update_data(start_dist=start_dist)
                await state.update_data(finish_dist=finish_dist)
                await state.update_data(number_of_hotels=number_of_hotels)

                await message.answer(
                    f'Введите количество отелей, которое необходимо вывести в '
                    f'результате, '
                    f'но не больше {valid_hotels_counter}')

                await state.set_state('input_hotels_amount_bestdeal')

            elif valid_hotels_counter == 0:
                await message.answer(
                    f'Найдено 0 отелей по заданным параметрам\n'
                    f'Попробуйте еще раз /bestdeal')
                await state.finish()
        else:
            await message.answer(f'Найдено 0 отелей по заданным параметрам\n'
                                 f'Попробовать еще раз /bestdeal')
            await state.finish()

    except Exception as e:
        logging.exception(e)
        await message.answer(f'Некорректные данные для поиска\n'
                             f'Попробовать еще раз /bestdeal')
        await state.finish()


@dp.message_handler(regexp='\d+', state='input_hotels_amount_bestdeal')
async def input_hotels_amount_func(message: types.Message, state: FSMContext):
    try:
        logging.info(f'{message.from_user.id} {message.text}')

        data = await state.get_data()
        number_of_hotels = int(data.get('number_of_hotels'))
        hotels_amount = int(message.text)

        if (hotels_amount <= number_of_hotels) and (hotels_amount > 0):
            await state.update_data(hotels_amount=hotels_amount)

            await message.answer('Вывести фотографии для каждого отеля?',
                                 reply_markup=photos_keyboard)

            await state.set_state('input_photos_bestdeal')
        else:
            await message.answer('Некорректное количество отелей для поиска\n'
                                 'Попробуйте еще раз /bestdeal')
            await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.callback_query_handler(state='input_photos_bestdeal')
async def show_low_price_hotels(call: CallbackQuery, state: FSMContext):
    try:
        logging.info(f'{call.from_user.id} {call.data}')

        await call.answer()
        # 10 - это ограничение колиичества фотографий для Телеграм поста
        temp_hotel_amount = 10
        # Из колбека (то что передается через кнопку) берем состояние (
        # photos_yes или photos_no)

        if call.data == 'photos_yes':
            await call.message.answer(f'Введите количество фотографий, '
                                      f'которое будет выводиться с каждым '
                                      f'отелем, но не больше '
                                      f'{temp_hotel_amount}')

            await state.set_state('input_photo_amount_bestdeal')
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

                        hotel_description += f'Название отеля: {hotel_name}\n' \
                                             f'Адрес отеля: {hotel_address}\n' \
                                             f'Расстояние от центра города: ' \
                                             f'{hotel_distance} \n' \
                                             f'Цена за сутки: {hotel_price}'
                        # name=hotel_name,
                        # address=hotel_address,
                        # distance=hotel_distance,
                        # price=hotel_price)
                        counter += 1
                        hotels_history += hotel_name + '\n'
                    except Exception as e:
                        logging.exception(e)
                        continue
                else:
                    break

            command_datetime = data.get('command_datetime')
            command = data.get('command')
            # Добавляем запись в БД для истории поиска
            db.add_history(call.from_user.id, command, command_datetime,
                           hotels_history)

            await call.message.answer(hotel_description)
            await state.finish()

    except Exception as e:
        logging.exception(e)
        await state.finish()


@dp.message_handler(regexp='\d+', state='input_photo_amount_bestdeal')
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
                    # Создаем медиагруппу для ТГ поста, в нее могут входить
                    # не только фотки
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
                            # Изначально ссылка неликвидная, туда вместе {
                            # size} навдо подставить букву, указываю размер
                            # фотки
                            photo_link = photo['baseUrl']
                            # Берем фотку с параметром z, это определенный
                            # размер, там другие буквы - другие разрешения фоток
                            new_photo_link = photo_link.replace('{size}', 'z')
                            # Чтобы отображалось описание в посте с альбомом,
                            # необходимо вставить его в последнюю фотку
                            # Поэтому если последняя фотка, то вставляем
                            # описание
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
                                # Добавляем в пост фото, здесь с названием,
                                # так как
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
