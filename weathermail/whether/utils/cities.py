from whether.models import Location
from json import JSONDecodeError
import logging
import requests

API_URL = 'https://public.opendatasoft.com/api/records/1.0/search/'
PARAMS = {
    'dataset': '1000-largest-us-cities-by-population-with-geographic-coordinates',
    'rows': '100',
    'sort': '-rank',
}


def _parse_city_data_from_response(r):
    """Get city data from a response object

    Arguments:
        r {response} -- response object which has city data

    Returns:
        list of dicts -- data for 100 most populous cities
    """
    logging.info('Parsing city data from reponse')
    try:
        response_data = r.json()
        records = response_data['records']
        # list of dicts of city data
        largest_cities = [
            {'city': r['fields']['city'],
             'state': r['fields']['state'],
             'population': r['fields']['population']
             } for r in records
        ]
    except (KeyError, JSONDecodeError):
        logging.error('City data not found in response', exc_info=True)
        return
    return largest_cities


def _get_cities_from_api():
    """Hits API to get top 100 most populous cities

    Returns:
        list of dicts -- data for 100 most populous cities
    """
    logging.info('Downloading city data')
    try:
        r = requests.get(API_URL, params=PARAMS)

    # If this API download occasionally fails, that's fine. Cities don't change
    # population rank enough to make missing an update a critical error
    except requests.exceptions.RequestException:
        logging.error('Error when trying to download cities data', exc_info=True)
        return
    logging.info('City data downloaded')

    return _parse_city_data_from_response(r)


def _add_new_cities_to_db_and_update_population(largest_cities):
    """Creates new cities that don't yet exist, and updates the population of
    all cities in the db

    Arguments:
        largest_cities (list of dicts) -- data for 100 most populous cities
    """

    logging.info('Creating new location objects')
    locations = [Location(**city_info) for city_info in largest_cities]
    Location.objects.bulk_create(locations, ignore_conflicts=True)
    logging.info('New location objects created')

    logging.info('Updating population of all cities')
    for l in locations:
        # update works on querysets, can't update on an individual object unless it's in a queryset
        Location.objects.filter(city=l.city, state=l.state).update(population=l.population)
    logging.info('City populations updated')


def load_cities():
    """Grab a list of the top 100 cities by population, and make sure they all exist in the db
    """
    largest_cities = _get_cities_from_api()
    if largest_cities:
        _add_new_cities_to_db_and_update_population(largest_cities)
