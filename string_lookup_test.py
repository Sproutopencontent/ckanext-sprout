from string_lookup import StringLookup

strings = StringLookup('test_strings.json')

def test_lookup_valid_weather_code():
    # Ensure this works the same with both string and numeric codes
    assert isinstance(strings.lookup_weather_code('1000'), str)
    assert isinstance(strings.lookup_weather_code(1000), str)
    assert strings.lookup_weather_code('1000') == strings.lookup_weather_code(1000)
    # Make sure it's different from the "not found" value
    assert strings.lookup_weather_code(1000) != strings.lookup_weather_code(9999999)

def test_lookup_invalid_weather_code():
    # No matter the value, if it's invalid, it should work but always return the same string
    assert isinstance(strings.lookup_weather_code('abc'), str)
    assert isinstance(strings.lookup_weather_code(9999999), str)
    assert strings.lookup_weather_code('abc') == strings.lookup_weather_code(9999999)

def test_lookup_valid_day():
    assert isinstance(strings.lookup_day_name(5), str)
    assert isinstance(strings.lookup_day_name('5'), str)
    assert strings.lookup_day_name(5) == strings.lookup_day_name('5')
    assert strings.lookup_day_name(5) != strings.lookup_day_name(900)

def test_lookup_invalid_day():
    assert isinstance(strings.lookup_day_name('800'), str)
    assert isinstance(strings.lookup_day_name(900), str)
    assert strings.lookup_day_name('800') == strings.lookup_day_name(900)

def test_lookup_valid_flood_index():
    assert isinstance(strings.lookup_flood_index('3'), str)
    assert isinstance(strings.lookup_flood_index(3), str)
    assert strings.lookup_flood_index('3') == strings.lookup_flood_index(3)
    assert strings.lookup_flood_index(3) != strings.lookup_flood_index(300)

def test_lookup_invalid_flood_index():
    assert isinstance(strings.lookup_flood_index('300'), str)
    assert isinstance(strings.lookup_flood_index(400), str)
    assert strings.lookup_flood_index('300') == strings.lookup_flood_index(400)
