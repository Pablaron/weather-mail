from django.test import TestCase
from requests.exceptions import RequestException
from unittest.mock import patch
from whether.factories import (
    LocationFactory,
    WeatherFactory,
)
from whether.models import Location
from whether.utils.weather import (
    _download_weather_data,
    _get_weather_from_response,
    get_cities_with_good_weather,
    get_cities_with_crummy_weather,
    get_all_other_cities,
)

import requests
import responses


class TestDownloadWeatherData(TestCase):

    @patch('whether.utils.weather.requests.get')
    def test_api_hit(self, patch_requests_get):
        loc = LocationFactory()
        _download_weather_data(loc)
        assert patch_requests_get.called

    @patch('whether.utils.weather.requests.get')
    def test_error_on_bad_request(self, patch_requests_get):
        loc = LocationFactory()
        patch_requests_get.side_effect = RequestException()
        ret = _download_weather_data(loc)
        self.assertIsNone(ret)


class TestGetWeatherFromResponse(TestCase):

    @responses.activate
    def test_error_when_no_data(self):
        responses.add(responses.GET, 'http://url', json={'error': 'not found'}, status=404)
        resp = requests.get('http://url')
        loc = LocationFactory()
        ret = _get_weather_from_response(resp, loc)
        [self.assertEqual(None, v) for k, v in ret.items()]

    @responses.activate
    def test_key_error_when_corrupt_data(self):
        responses.add(responses.GET, 'http://url', json={'data': [{'temp': '2'}, {'temp': '1'}]}, status=404)
        resp = requests.get('http://url')
        loc = LocationFactory()
        ret = _get_weather_from_response(resp, loc)
        [self.assertEqual(None, v) for k, v in ret.items()]

    @responses.activate
    def test_parsed_data_correctly_formatted(self):
        request_return_data = [
            {'high_temp': '2',
             'weather': {
                'code': '123',
                'description': 'desc',
                'icon': 'icon.pic'
                },
             },
            {'high_temp': '3',
             'weather': {
                'code': '321',
                'description': 'disc',
                'icon': 'ican.pic'
                },
             }
        ]
        responses.add(responses.GET, 'http://url', json={'data': request_return_data}, status=200)
        resp = requests.get('http://url')
        expected = {
            'temperature_today': '2',
            'weather_code': '123',
            'weather_description': 'desc',
            'weather_icon': 'icon.pic',
            'temperature_tomorrow': '3'
        }
        loc = LocationFactory()
        ret = _get_weather_from_response(resp, loc)
        self.assertEqual(ret, expected)


class TestGetCitiesWithGoodWeather(TestCase):

    def test_five_degrees_warmer_than_tomorrow(self):
        w = WeatherFactory(temperature_today=60, temperature_tomorrow=55)
        expected = [w.location]
        ret = get_cities_with_good_weather()
        self.assertEqual(ret, expected)

    def test_sunny(self):
        w = WeatherFactory(temperature_today=55, temperature_tomorrow=55, weather_code=800)
        expected = [w.location]
        ret = get_cities_with_good_weather()
        self.assertEqual(ret, expected)


class TestGetCitiesWithBadWeather(TestCase):

    def test_five_degrees_cooler_than_tomorrow(self):
        w = WeatherFactory(temperature_today=50, temperature_tomorrow=55, weather_code=800)
        good_weather = []
        expected = [w.location]
        ret = get_cities_with_crummy_weather(good_weather)
        self.assertEqual(ret, expected)

    def test_precipitating(self):
        w = WeatherFactory(temperature_today=55, temperature_tomorrow=55, weather_code=700)
        good_weather = []
        expected = [w.location]
        ret = get_cities_with_crummy_weather(good_weather)
        self.assertEqual(ret, expected)

    def test_dont_choose_users_in_good_weather(self):
        w = WeatherFactory(temperature_today=60, temperature_tomorrow=55, weather_code=800)
        good_weather = [w.location]
        expected = []
        ret = get_cities_with_crummy_weather(good_weather)
        self.assertEqual(ret, expected)


class TestGetAllOtherCities(TestCase):

    def test_get_all_locations_not_in_good_or_bad_weather(self):
        good_weather = WeatherFactory(temperature_today=60, temperature_tomorrow=55)
        poor_weather = WeatherFactory(temperature_today=50, temperature_tomorrow=55)
        good = [good_weather.location]
        poor = [poor_weather.location]
        expected = [l for l in Location.objects.all() if l not in good and l not in poor]
        ret = get_all_other_cities(good, poor)
        self.assertEqual(ret, expected)
