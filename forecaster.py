from datetime import datetime
import json
import logging
import os
import requests
from string_lookup import *

class ForecasterConfig:
    def __init__(self, env):
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'INFO')
        self.API_KEY = env.get('TOMORROW_API_KEY')
        self.API_URL = env.get('TOMORROW_API_URL', 'https://api.tomorrow.io/v4')
        self.STRINGS_FILE = env.get('STRINGS_FILE', 'english.json')
        self.TIMEZONE_NAME = env.get('TZ', 'Africa/Nairobi')

class Forecaster:
    def __init__(self, config):
        self.config = config
        self.strings = StringLookup(config.STRINGS_FILE)
        self.api_session = requests.session()

    def get_daily_forecasts(self, latlng):
        params = {
            'apikey': self.config.API_KEY,
            # We only want a week of data, starting tomorrow
            'startTime': 'nowPlus1d',
            'endTime': 'nowPlus7d',
            'fields': ['floodIndex', 'weatherCode'],
            'location': f'{latlng[0]},{latlng[1]}',
            'timesteps': '1d',
            'timezone': self.config.TIMEZONE_NAME,
            'units': 'metric'
        }
        try:
            response = self.api_session.get(
                f'{self.config.API_URL}/timelines',
                params=params,
                timeout=10.0
            )
            response_body = response.json()
            logging.debug(json.dumps(response_body, indent=2))
            # Return just the data
            return response_body['data']['timelines'][0]['intervals']
        except requests.exceptions.RequestException:
            logging.exception('Request error')

    def summarize_forecast(self, forecast):
        flood_index = forecast['values'].get('floodIndex', 0)

        # Flood index takes precedence when greater than zero
        if flood_index > 0:
            return self.strings.lookup_flood_index(flood_index)
        return self.strings.lookup_weather_code(forecast['values']['weatherCode'])

    def is_same_forecast(self, forecast_a, forecast_b):
        return self.summarize_forecast(forecast_a) == self.summarize_forecast(forecast_b)

    def format_forecast_segment(self, first_forecast, last_forecast):
        first_day = datetime.fromisoformat(first_forecast['startTime']).weekday()
        last_day = datetime.fromisoformat(last_forecast['startTime']).weekday()
        summary = self.summarize_forecast(first_forecast)

        day_names = self.strings.lookup_day_name(first_day)
        if first_day != last_day:
            day_names += f'-{self.strings.lookup_day_name(last_day)}'
        return f'{day_names}:{summary}'

    def format_forecasts(self, forecasts):
        segments = []
        first_forecast_in_run = forecasts[0]
        last_forecast = None
        for forecast in forecasts:
            if last_forecast is not None and not self.is_same_forecast(first_forecast_in_run, forecast):
                # The forecast changed from yesterday, output the previous run
                segments.append(self.format_forecast_segment(first_forecast_in_run, last_forecast))
                first_forecast_in_run = forecast

            last_forecast = forecast

        # Output the final run
        segments.append(self.format_forecast_segment(first_forecast_in_run, last_forecast))
        return '. '.join(segments)


    def run(self):
        forecasts = self.get_daily_forecasts([-1.2874821, 36.8310251])
        print(self.format_forecasts(forecasts))

if __name__ == '__main__':
    # Configure from OS environment variables
    config = ForecasterConfig(os.environ)
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=config.LOG_LEVEL)
    Forecaster(config).run()
