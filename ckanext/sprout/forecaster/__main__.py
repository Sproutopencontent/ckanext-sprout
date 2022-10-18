import csv
import logging
import os
import sys
from .forecaster import Forecaster

# Configure from OS environment variables
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
API_KEY = os.environ.get('TOMORROW_API_KEY')
API_URL = os.environ.get('TOMORROW_API_URL', 'https://api.tomorrow.io/v4')
# Languages should use ISO 639-1 codes, see:
# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# Multiple languages can be specified by separating them with commas
LANGUAGES = os.environ.get('LANGUAGES', 'EN').split(',')
TIMEZONE = os.environ.get('TZ', 'Africa/Nairobi')

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=LOG_LEVEL,
    stream=sys.stderr
)
# Default is example_locations.csv in this directory, but can be overridden on the command line
locations_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'example_locations.csv')
if len(sys.argv) > 1:
    locations_file = sys.argv[1]

with open(locations_file, newline='') as locations_csv:
    writer = csv.writer(sys.stdout)
    forecaster = Forecaster(api_key=API_KEY, api_url=API_URL, languages=LANGUAGES, timezone=TIMEZONE)
    for row in forecaster.run(locations_csv):
        writer.writerow(row.values())
