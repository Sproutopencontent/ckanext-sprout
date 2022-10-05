from datetime import datetime
import json
import logging
from os import environ
import requests

api_key = environ.get('TOMORROW_API_KEY')
api_url = environ.get('TOMORROW_API_URL', 'https://api.tomorrow.io/v4')
strings_file = environ.get('WEATHER_CODE_FILE', 'english.json')
log_level = environ.get('LOG_LEVEL', 'INFO')
timezone_name = environ.get('TZ', 'Africa/Nairobi')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=log_level)

api_session = requests.session()
strings = None

class StringLookup:
    data = {}
    def __init__(self, file_name):
        with open(file_name) as raw_file:
            self.data = json.load(raw_file)

    def lookup_weather_code(self, code):
        return self.data['weatherCodeFullDay'].get(str(code), '?')

    def lookup_day_name(self, day):
        return self.data['day'].get(str(day), '?')

    def lookup_flood_index(self, index):
        return self.data['floodIndex'].get(str(index), '?')

def get_daily_forecasts(latlng, timezone):
    params = {
        'apikey': api_key,
        # We only want a week of data
        'endTime': 'nowPlus7d',
        'fields': [
            'cloudCoverAvg',
            'precipitationIntensityAvg',
            'precipitationProbabilityAvg',
            'floodIndex',
            'weatherCodeFullDay'
        ],
        'location': f'{latlng[0]},{latlng[1]}',
        'timesteps': '1d',
        'timezone': timezone,
        'units': 'metric'
    }
    try:
        response = api_session.get(f'{api_url}/timelines', params=params, timeout=10.0)
        response_body = response.json()
        logging.debug(json.dumps(response_body, indent=2))
        # Return just the data
        return response_body['data']['timelines'][0]['intervals']
    except requests.exceptions.RequestException:
        logging.exception('Request error')

def is_same_forecast(forecast_a, forecast_b):
    flood_index_a = forecast_a['values'].get('floodIndex', 0)
    flood_index_b = forecast_b['values'].get('floodIndex', 0)

    # Flood index takes precedence when greater than zero
    if flood_index_a > 0 or flood_index_b > 0:
        return flood_index_a == flood_index_b

    summary_a = strings.lookup_weather_code(forecast_a['values']['weatherCodeFullDay'])
    summary_b = strings.lookup_weather_code(forecast_b['values']['weatherCodeFullDay'])

    return summary_a == summary_b

def format_forecast_segment(first_forecast, last_forecast):
    first_day = datetime.fromisoformat(first_forecast['startTime']).weekday()
    last_day = datetime.fromisoformat(last_forecast['startTime']).weekday()
    flood_index = first_forecast['values'].get('floodIndex', 0)

    # Flood index takes precedence when greater than zero
    if flood_index > 0:
        summary = strings.lookup_flood_index(flood_index)
    else:
        summary = strings.lookup_weather_code(first_forecast['values']['weatherCodeFullDay'])

    day_names = strings.lookup_day_name(first_day)
    if first_day != last_day:
        day_names += f'-{strings.lookup_day_name(last_day)}'
    return f'{day_names}:{summary}'

def format_forecasts(forecasts):
    segments = []
    first_forecast_in_run = forecasts[0]
    last_forecast = None
    for forecast in forecasts:
        if last_forecast is not None and not is_same_forecast(first_forecast_in_run, forecast):
            # The forecast changed from yesterday, output the previous run
            segments.append(format_forecast_segment(first_forecast_in_run, last_forecast))
            first_forecast_in_run = forecast

        last_forecast = forecast

    # Output the final run
    segments.append(format_forecast_segment(first_forecast_in_run, last_forecast))
    return '. '.join(segments)


def main():
    global strings
    strings = StringLookup(strings_file)
    forecasts = get_daily_forecasts([12.603018100000003, 37.42744581804207], timezone_name)
    print(format_forecasts(forecasts))

if __name__ == '__main__':
    main()
