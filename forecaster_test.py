from forecaster import Forecaster, ForecasterConfig

env = {
    'API_KEY': 'fakekey',
    'API_URL': 'http://localhost:9000',
    'STRINGS_FILE': 'test_strings.json',
}

forecast_sunny_a = {
    'startTime': '2022-10-06T06:00:00+03:00', # Thursday
    'values': {
        'floodIndex': 0,
        'weatherCode': 1000,
    }
}
forecast_sunny_b = {
    'startTime': '2022-10-07T06:00:00+03:00', # Friday
    'values': {
        'floodIndex': 0,
        'weatherCode': 1100,
    }
}
forecast_sunny_c = {
    'startTime': '2022-10-08T06:00:00+03:00', # Saturday
    'values': {
        'floodIndex': 0,
        'weatherCode': 1100,
    }
}
forecast_rain = {
    'startTime': '2022-10-09T06:00:00+03:00', # Sunday
    'values': {
        'floodIndex': 0,
        'weatherCode': 4212,
    }
}
forecast_flood_and_rain_a = {
    'startTime': '2022-10-10T06:00:00+03:00', # Monday
    'values': {
        'floodIndex': 3,
        'weatherCode': 4212,
    }
}
forecast_flood_and_rain_b = {
    'startTime': '2022-10-11T06:00:00+03:00', # Tuesday
    'values': {
        'floodIndex': 3,
        'weatherCode': 4202,
    }
}

forecaster = Forecaster(ForecasterConfig(env))

class TestIsSameForecast:
    def test_match_without_flood(self):
        assert forecaster.is_same_forecast(forecast_sunny_a, forecast_sunny_a)
        assert forecaster.is_same_forecast(forecast_sunny_a, forecast_sunny_b)

    def test_mismatch_without_flood(self):
        assert not forecaster.is_same_forecast(forecast_sunny_a, forecast_rain)

    def test_match_with_flood(self):
        assert forecaster.is_same_forecast(forecast_flood_and_rain_a, forecast_flood_and_rain_a)
        assert forecaster.is_same_forecast(forecast_flood_and_rain_a, forecast_flood_and_rain_b)

    def test_mismatch_with_flood(self):
        assert not forecaster.is_same_forecast(forecast_sunny_a, forecast_flood_and_rain_a)
        assert not forecaster.is_same_forecast(forecast_rain, forecast_flood_and_rain_a)

class TestFormatForecastSegment:
    def test_single_day_no_flood(self):
        output = forecaster.format_forecast_segment(forecast_sunny_a, forecast_sunny_a)
        assert output == 'Thu:Sunny'

    def test_multiple_days_no_flood(self):
        output = forecaster.format_forecast_segment(forecast_sunny_a, forecast_sunny_b)
        assert output == 'Thu-Fri:Sunny'

    def test_single_day_with_flood(self):
       output = forecaster.format_forecast_segment(forecast_flood_and_rain_a, forecast_flood_and_rain_a)
       assert output == 'Mon:Significant flooding possible'

    def test_multiple_days_with_flood(self):
       output = forecaster.format_forecast_segment(forecast_flood_and_rain_a, forecast_flood_and_rain_b)
       assert output == 'Mon-Tue:Significant flooding possible'

class TestFormatForecasts:
    def test_same_forecast_all_days(self):
        output = forecaster.format_forecasts([forecast_sunny_a, forecast_sunny_b, forecast_sunny_c])
        assert output == 'Thu-Sat:Sunny'

    def test_different_forecast_all_days(self):
        output = forecaster.format_forecasts([
            forecast_sunny_c,
            forecast_rain,
            forecast_flood_and_rain_a
        ])
        assert output == 'Sat:Sunny. Sun:Heavy rain. Mon:Significant flooding possible'

    def test_multiple_groups(self):
        output = forecaster.format_forecasts([
            forecast_sunny_a,
            forecast_sunny_b,
            forecast_sunny_c,
            forecast_rain,
            forecast_flood_and_rain_a,
            forecast_flood_and_rain_b
        ])
        assert output == 'Thu-Sat:Sunny. Sun:Heavy rain. Mon-Tue:Significant flooding possible'
