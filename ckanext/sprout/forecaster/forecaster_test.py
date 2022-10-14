from forecaster import Forecaster, ForecasterConfig

env = {
    'API_KEY': 'fakekey',
    'API_URL': 'http://localhost:9000',
    'LANGUAGES': 'eng_test,fra_test',
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

class TestFormatForecasts:
    def test_single_day(self):
        output = forecaster.format_forecasts([forecast_sunny_a], 'eng_test')
        assert output == 'Thu:Sunny'

    def test_single_day_with_flooding(self):
        output = forecaster.format_forecasts([forecast_flood_and_rain_a], 'eng_test')
        assert output == 'Mon:Significant flooding possible'

    def test_multiple_days_same_forecast(self):
        output = forecaster.format_forecasts(
            [forecast_sunny_a, forecast_sunny_b, forecast_sunny_c],
            'eng_test'
        )
        assert output == 'Thu-Sat:Sunny'

    def test_different_forecast_all_days(self):
        output = forecaster.format_forecasts([
            forecast_sunny_c,
            forecast_rain,
            forecast_flood_and_rain_a
        ], 'eng_test')
        assert output == 'Sat:Sunny. Sun:Heavy rain. Mon:Significant flooding possible'

    def test_multiple_groups(self):
        output = forecaster.format_forecasts([
            forecast_sunny_a,
            forecast_sunny_b,
            forecast_sunny_c,
            forecast_rain,
            forecast_flood_and_rain_a,
            forecast_flood_and_rain_b
        ], 'eng_test')
        assert output == 'Thu-Sat:Sunny. Sun:Heavy rain. Mon-Tue:Significant flooding possible'

    def test_alternate_language(self):
        output = forecaster.format_forecasts([
            forecast_sunny_a,
            forecast_sunny_b,
            forecast_sunny_c,
            forecast_rain,
            forecast_flood_and_rain_a,
            forecast_flood_and_rain_b
        ], 'fra_test')
        assert output == 'Jeu-Sam:Ensoleillé. Dim:Forte pluie. Lun-Mar:Inondation considérable possible'
