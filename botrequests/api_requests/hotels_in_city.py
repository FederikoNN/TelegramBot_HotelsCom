import requests

from config import RAPID_API_KEY


def hotels_in_city(city):
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": city, "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()['suggestions'][0]['entities'][0]['destinationId']
