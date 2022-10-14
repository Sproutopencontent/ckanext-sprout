# Forecaster

This script takes weather forecasts from the tomorrow.io weather API and turns them into short, easily understood forecasts for the next 7 days that can (ideally) fit in a text message.

This script is using `pipenv`. To start working with it:
```
pipenv install
pipenv shell
```

Once inside the shell, you can just run the script:
```
python forecaster.py
```

or the tests:
```
pytest
```

To set environment variables like the API key (in POSIX-like shells, anyway), you can specify them before the command:
```
LOG_LEVEL=DEBUG TOMORROW_API_KEY=mysecretkey python forecaster.py
```
