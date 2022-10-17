import csv
from datetime import datetime
import json
import logging
import os
import requests
from .string_lookup import StringLookup

class Forecaster:
    def __init__(
        self,
        api_key,
        api_url='https://api.tomorrow.io/v4',
        languages=['en'],
        timezone='Africa/Nairobi'
    ):
        my_dir = os.path.dirname(os.path.realpath(__file__))

        self.api_session = requests.session()
        self.api_url = api_url
        self.default_api_params = {
            'apikey': api_key,
            'timezone': f'{timezone}'
        }
        self.strings = {
            lang.lower(): StringLookup(f'{my_dir}/lang/{lang.lower()}.json')
            for lang in languages
        }

    def get_daily_forecasts(self, latlng):
        params = {
            **self.default_api_params,
            # We only want a week of data, starting tomorrow
            'startTime': 'nowPlus1d',
            'endTime': 'nowPlus7d',
            'fields': ['floodIndex', 'weatherCode'],
            'location': f'{latlng[0]},{latlng[1]}',
            'timesteps': '1d',
            'units': 'metric'
        }
        try:
            response = self.api_session.get(
                f'{self.api_url}/timelines',
                params=params,
                timeout=10.0
            )
            response_body = response.json()
            logging.debug(json.dumps(response_body, indent=2))
            # Return just the data
            return response_body['data']['timelines'][0]['intervals']
        except requests.exceptions.RequestException:
            logging.exception('Request error')

    def summarize_forecast(self, forecast, lang):
        flood_index = forecast['values'].get('floodIndex', 0)

        # Flood index takes precedence when greater than zero
        if flood_index > 0:
            return self.strings[lang].lookup_flood_index(flood_index)
        return self.strings[lang].lookup_weather_code(forecast['values']['weatherCode'])

    def is_same_forecast(self, forecast_a, forecast_b, lang):
        return self.summarize_forecast(forecast_a, lang) == self.summarize_forecast(forecast_b, lang)

    def format_forecast_segment(self, first_forecast, last_forecast, lang):
        first_day = datetime.fromisoformat(first_forecast['startTime']).weekday()
        last_day = datetime.fromisoformat(last_forecast['startTime']).weekday()
        summary = self.summarize_forecast(first_forecast, lang)

        day_names = self.strings[lang].lookup_day_name(first_day)
        if first_day != last_day:
            day_names += f'-{self.strings[lang].lookup_day_name(last_day)}'
        return f'{day_names}:{summary}'

    def summarize_forecasts(self, forecasts, lang):
        segments = []
        first_forecast_in_run = forecasts[0]
        last_forecast = None
        for forecast in forecasts:
            if last_forecast is not None and not self.is_same_forecast(first_forecast_in_run, forecast, lang):
                # The forecast changed from yesterday, output the previous run
                segments.append(self.format_forecast_segment(first_forecast_in_run, last_forecast, lang))
                first_forecast_in_run = forecast

            last_forecast = forecast

        # Output the final run
        segments.append(self.format_forecast_segment(first_forecast_in_run, last_forecast, lang))
        return '. '.join(segments)

    def run(self, locations_csv):
        locations_reader = csv.DictReader(locations_csv)

        for row in locations_reader:
            # Each row must at least include a latitude and longitude field.
            forecasts = self.get_daily_forecasts([row['latitude'], row['longitude']])
            row.update({
                f'forecast_{lang}': self.summarize_forecasts(forecasts, lang)
                for lang in self.strings.keys()
            })
            yield row
