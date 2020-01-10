from dal import autocomplete
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from whether.models import Location, Subscriber
from whether.forms import SubscriberForm


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Location.objects.all()
        if self.q:
            qs = qs.filter(city__icontains=self.q) | qs.filter(state__icontains=self.q)
        return qs


class SubscribeView(generic.CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'whether/subscribe.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('success', kwargs={'subscriber_id': self.object.pk})


class UpdateView(generic.UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'whether/subscribe.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('success', kwargs={'subscriber_id': self.object.pk})


def success(request, **kwargs):
    subscriber = get_object_or_404(Subscriber, pk=kwargs['subscriber_id'])
    location = subscriber.location.city
    return render(request, 'whether/success.html', {'subscriber': subscriber, 'location': location})
