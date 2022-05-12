import requests

from config import RAPID_API_KEY


def hotel_photos(hotel):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()
