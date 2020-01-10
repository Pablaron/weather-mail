from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from factory import fuzzy
from whether.models import Location, Subscriber, Weather
import factory


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    city = factory.fuzzy.FuzzyText(length=12)
    state = factory.fuzzy.FuzzyText(length=12)
    population = factory.fuzzy.FuzzyInteger(1)


class SubscriberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscriber

    email = factory.fuzzy.FuzzyText(length=12, suffix='@gmail.com')
    location = factory.SubFactory(LocationFactory)


class WeatherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Weather

    location = factory.SubFactory(LocationFactory)
    weather_code = factory.fuzzy.FuzzyInteger(1)
    weather_icon = factory.fuzzy.FuzzyText(length=6)
    weather_description = factory.fuzzy.FuzzyText(length=255)
    temperature_today = factory.fuzzy.FuzzyInteger(1)
    temperature_tomorrow = factory.fuzzy.FuzzyInteger(1)
