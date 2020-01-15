from django.conf import settings
from django.db.models import F
from json import JSONDecodeError
from requests.exceptions import RequestException
from whether.models import Location, Weather
from whether.utils.weather_codes import NICE_WEATHER, NON_PRECIPITATION
import datetime
import logging
import requests

FORECAST_BASE_URL = 'http://api.weatherbit.io/v2.0/forecast/daily'
WEATHER_ARGS = {
    'units': 'I',
    'key': settings.WEATHERBIT_KEY,
    'country': 'US',
}


def _download_weather_data(location):
    """Downloads weather data from the Weatherbit API

    Arguments:
        location {Location} -- Location to download data for

    Returns:
        response -- Requests response object from Weatherbit API
    """
    params = WEATHER_ARGS.copy()
    params['city'] = f'{location.city},{location.state}'
    try:
        r = requests.get(url=FORECAST_BASE_URL, params=params)
    except RequestException:
        logging.error(f'Failed to download weather for {location}.', exc_info=True)
        return None
    return r


def _get_weather_from_response(r, location):
    """Returns parsed data from the API response

    Arguments:
        r {Requests response object}

    Returns:
        dict -- data needed for a Weather object
    """
    try:
        # API pulls in chronological order - ['data'][0] is today, ['data'][1] tomorrows
        current_conditions = r.json()['data'][0]
        forecast = r.json()['data'][1]
        weather_data = {
            'temperature_today': current_conditions['high_temp'],
            'weather_code': current_conditions['weather']['code'],
            'weather_description': current_conditions['weather']['description'],
            'weather_icon': current_conditions['weather']['icon'],
            'temperature_tomorrow': forecast['high_temp']
        }
    except (KeyError, JSONDecodeError):
        logging.error(f'Missing data from response. Clearing weather data for {location}', exc_info=True)
        weather_data = {
            'temperature_today': None,
            'weather_code': None,
            'weather_description': None,
            'weather_icon': None,
            'temperature_tomorrow': None
        }
    return weather_data


def update_weather():
    """For each location in the db, grab the weather from weatherbit, and update
    the weather in the db
    """
    for location in Location.objects.all():
        weather, created = Weather.objects.get_or_create(location=location)
        # Limited API calls mean we want to update at most once per day
        if weather.updated_ts.date() >= datetime.date.today() and not created:
            logging.warning(f'Weather data already created today for {weather.location}. Skipping.')
            continue

        # Download and parse data, then update the Weather object with this info
        r = _download_weather_data(location)
        if r:
            weather_data = _get_weather_from_response(r, location)
            Weather.objects.filter(pk=weather.pk).update(**weather_data)


def weather_valid(l):
    # Must compare to None since a temperature value = 0 is not truthy
    if l.temperature_today is None or l.temperature_tomorrow is None\
        or l.weather_code is None or l.weather_description is None:
        return False
    return True


def get_cities_with_good_weather():
    """Return all cities with:
    todays temp >= tomorrows temp + 5 OR the sky is "scattered clouds" or more clear

    Returns:
        list of Locations -- that fall into the "good" criteria
    """
    good_weather = Weather.objects.filter(temperature_today__gte=F('temperature_tomorrow')+5) | \
        Weather.objects.filter(weather_code__in=NICE_WEATHER)
    return [w.location for w in good_weather if weather_valid(w)]


def get_cities_with_crummy_weather(good_weather_cities):
    """Return all cities with:
    (todays temp <= tomorrows temp - 5 OR it is precipitating) AND not in good_weather_cities

    Returns:
        list of Locations -- that fall into the "crummy" criteria
    """
    bad_weather_candidates = Weather.objects.filter(temperature_today__lte=F('temperature_tomorrow')-5) | \
        Weather.objects.exclude(weather_code__in=NON_PRECIPITATION)
    return [w.location for w in bad_weather_candidates if w not in good_weather_cities and weather_valid(w)]


def get_all_other_cities(good_weather_cities, bad_weather_cities):
    """Return all cities:
    NOT IN (good_weather_cities U bad_weather_cities)

    Returns:
        list of Locations -- that fall into neither "good" nor "crummy" criteria
    """
    all_cities = Location.objects.all()
    return [l for l in all_cities if l not in good_weather_cities and l not in bad_weather_cities]
