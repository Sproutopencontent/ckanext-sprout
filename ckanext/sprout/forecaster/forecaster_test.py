from .forecaster import Forecaster
import pytest

# Constants

locations_csv = ['latitude,longitude', '0.0,0.0']

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

# Helper functions

def make_response(forecasts):
    return {
        'data': {
            'timelines': [{
                'intervals': forecasts
            }]
        }
    }

# Fixtures

@pytest.fixture
def forecaster(httpserver):
    return Forecaster(
        api_key='testkey',
        api_url=f'http://{httpserver.host}:{httpserver.port}',
        languages='en_test,fr_test'
    )

# Tests

def test_single_day(httpserver, forecaster):
    httpserver.expect_request('/timelines').respond_with_json(make_response([
        forecast_sunny_a
    ]))
    assert list(forecaster.run(locations_csv)) == [{
        'latitude': '0.0',
        'longitude': '0.0',
        'forecast_en_test': 'Thu:Sunny',
        'forecast_fr_test': 'Jeu:Ensoleillé'
    }]

def test_single_day_with_flooding(httpserver, forecaster):
    httpserver.expect_request('/timelines').respond_with_json(make_response([
        forecast_flood_and_rain_a
    ]))
    assert list(forecaster.run(locations_csv)) == [{
        'latitude': '0.0',
        'longitude': '0.0',
        'forecast_en_test': 'Mon:Significant flooding possible',
        'forecast_fr_test': 'Lun:Inondation considérable possible'
    }]

def test_multiple_days_same_forecast(httpserver, forecaster):
    httpserver.expect_request('/timelines').respond_with_json(make_response([
        forecast_sunny_a, forecast_sunny_b, forecast_sunny_c
    ]))
    assert list(forecaster.run(locations_csv)) == [{
        'latitude': '0.0',
        'longitude': '0.0',
        'forecast_en_test': 'Thu-Sat:Sunny',
        'forecast_fr_test': 'Jeu-Sam:Ensoleillé'
    }]

def test_different_forecast_all_days(httpserver, forecaster):
    httpserver.expect_request('/timelines').respond_with_json(make_response([
        forecast_sunny_c, forecast_rain, forecast_flood_and_rain_a
    ]))
    assert list(forecaster.run(locations_csv)) == [{
        'latitude': '0.0',
        'longitude': '0.0',
        'forecast_en_test': 'Sat:Sunny. Sun:Heavy rain. Mon:Significant flooding possible',
        'forecast_fr_test': 'Sam:Ensoleillé. Dim:Forte pluie. Lun:Inondation considérable possible'
    }]

def test_multiple_groups(httpserver, forecaster):
    httpserver.expect_request('/timelines').respond_with_json(make_response([
        forecast_sunny_a,
        forecast_sunny_b,
        forecast_sunny_c,
        forecast_rain,
        forecast_flood_and_rain_a,
        forecast_flood_and_rain_b
    ]))
    assert list(forecaster.run(locations_csv)) == [{
        'latitude': '0.0',
        'longitude': '0.0',
        'forecast_en_test': 'Thu-Sat:Sunny. Sun:Heavy rain. Mon-Tue:Significant flooding possible',
        'forecast_fr_test': 'Jeu-Sam:Ensoleillé. Dim:Forte pluie. Lun-Mar:Inondation considérable possible'
    }]
