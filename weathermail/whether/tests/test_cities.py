from django.test import TestCase
from requests.exceptions import RequestException
from unittest.mock import patch
from whether.models import Location
from whether.utils.cities import (
    _get_cities_from_api,
    _parse_city_data_from_response,
    _add_new_cities_to_db_and_update_population,
)
import requests
import responses


class TestParseCityDataFromResponse(TestCase):

    @responses.activate
    def test_pulls_out_correct_data_from_response(self):
        resp_data = [{
                        'fields': {
                            'city': 'boston',
                            'state': 'ma',
                            'population': '10',
                        }
                    }]
        expected = [{
            'city': 'boston',
            'state': 'ma',
            'population': '10',
        }]
        responses.add(responses.GET, 'http://url', json={'records': resp_data}, status=200)
        resp = requests.get('http://url')
        ret = _parse_city_data_from_response(resp)
        self.assertEqual(expected, ret)

    @responses.activate
    def test_errors_when_data_not_found(self):
        responses.add(responses.GET, 'http://url', json={'error': 'not found'}, status=404)
        resp = requests.get('http://url')
        ret = _parse_city_data_from_response(resp)
        self.assertIsNone(ret)


class TestGetCitiesFromAPI(TestCase):

    @patch('whether.utils.cities._parse_city_data_from_response')
    @patch('whether.utils.cities.requests.get')
    def test_api_hit(self, patch_get, patch_parse):
        _get_cities_from_api()
        assert patch_get.called
        assert patch_parse.called

    @patch('whether.utils.cities._parse_city_data_from_response')
    @patch('whether.utils.cities.requests.get')
    def test_exception_on_api_error(self, patch_get, patch_parse):
        patch_get.side_effect = RequestException()
        assert not patch_parse.called


class TestAddToDatabase(TestCase):

    def test_new_cities_are_added(self):
        city_info = [{
            'city': 'Beantown',
            'state': 'Mass',
            'population': '100'
        }]
        Location.objects.all().delete()
        _add_new_cities_to_db_and_update_population(city_info)
        self.assertEqual(1, len(Location.objects.all()))

    def test_all_cities_are_updated(self):
        city_info = [{
            'city': 'Beantown',
            'state': 'Mass',
            'population': '100'
        }]
        Location.objects.all().delete()
        _add_new_cities_to_db_and_update_population(city_info)
        city_info = [{
            'city': 'Beantown',
            'state': 'Mass',
            'population': '200'
        }]
        _add_new_cities_to_db_and_update_population(city_info)
        self.assertEqual(200, Location.objects.first().population)
