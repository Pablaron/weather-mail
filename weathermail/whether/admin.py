from django.contrib import admin
from whether.models import (
    Location,
    Subscriber,
    Weather,
)
from whether.forms import SubscriberForm


class SubscriberAdmin(admin.ModelAdmin):
    form = SubscriberForm


admin.site.register(Location)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Weather)
