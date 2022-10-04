import json
import logging
from os import environ
import requests
import sys

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

api_url = environ.get('TOMORROW_API_URL', 'https://api.tomorrow.io/v4')
api_key = environ.get('TOMORROW_API_KEY')

api_session = requests.session()

def get_daily_forecast(latlng, timezone='Africa/Nairobi'):
    params = {
        'apikey': api_key,
        'fields': [
            'precipitationIntensity',
            'precipitationProbability',
            'floodIndex',
            'weatherCodeFullDay'
        ],
        'location': f'{latlng[0]},{latlng[1]}',
        'timesteps': '1d',
        'timezone': timezone,
        'units': 'metric'
    }
    try:
        return api_session.get(f'{api_url}/timelines', params=params).json()
    except requests.exceptions.RequestException:
        logging.exception('Server error')

def main():
    json.dump(get_daily_forecast([12.603018100000003, 37.42744581804207]), sys.stdout, indent=2)

if __name__ == '__main__':
    main()
