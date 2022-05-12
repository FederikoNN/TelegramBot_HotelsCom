from datetime import datetime, timedelta

import requests

from config import RAPID_API_KEY


def hotels_list(city, sort):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    querystring = {"destinationId": city,
                   "pageNumber": "1",
                   "pageSize": "25",
                   "checkIn": today,
                   "checkOut": tomorrow,
                   "adults1": "1",
                   "sortOrder": sort,
                   "locale": "ru_RU",
                   "currency": "RUB"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()['data']['body']['searchResults']['results']


def hotels_list_price_distance(city, start_price, finish_price):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    querystring = {"destinationId": city,
                   "pageNumber": "1",
                   "pageSize": "25",
                   "checkIn": today,
                   "checkOut": tomorrow,
                   "adults1": "1",
                   "sortOrder": "PRICE",
                   "locale": "ru_RU",
                   "currency": "RUB",
                   "priceMin": start_price,
                   "priceMax": finish_price
                   }

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()['data']['body']['searchResults']['results']
