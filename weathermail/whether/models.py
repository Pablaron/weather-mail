from django.db import models


class Location(models.Model):

    class Meta:
        ordering = ['-population']  # Most populous results will show up first in autocomplete
        unique_together = ('city', 'state',)

    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    population = models.PositiveIntegerField()
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.city}, {self.state}'

    def __repr__(self):
        return f'{self.city}, {self.state}'


class Weather(models.Model):
    location = models.OneToOneField(to=Location, on_delete=models.CASCADE)
    weather_code = models.PositiveIntegerField(null=True, blank=True)
    weather_icon = models.CharField(max_length=6, null=True, blank=True)
    weather_description = models.TextField(null=True, blank=True)
    temperature_today = models.IntegerField(null=True, blank=True)
    temperature_tomorrow = models.IntegerField(null=True, blank=True)
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.location.city}: {self.temperature_today}*F, {self.weather_description}'


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    location = models.ForeignKey(to=Location, on_delete=models.SET_NULL, null=True)
    created_ts = models.DateTimeField(auto_now_add=True)
    updated_ts = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.email}: {self.location}'
