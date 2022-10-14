# Forecaster

This script takes weather forecasts from the tomorrow.io weather API and turns them into short, easily understood forecasts for the next 7 days that can (ideally) fit in a text message.

This script is using `pipenv`. To start working with it:
```
pipenv install
pipenv shell
```

Once inside the shell, you can run the module for testing, but note that you need to be in the parent directory. Here's how you can do that as a one-liner in most shells:
```
(cd .. && python -m forecaster)
```

or to run the tests (in this directory):
```
pipenv install --dev
pytest -v
```

To set environment variables like the API key (in POSIX-like shells, anyway), you can specify them before the command:
```
(cd .. && LOG_LEVEL=DEBUG TOMORROW_API_KEY=mysecretkey python -m forecaster)
```
