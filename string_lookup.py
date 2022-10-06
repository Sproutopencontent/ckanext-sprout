import json

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
