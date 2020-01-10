from dal import autocomplete
from django import forms
from whether.models import Subscriber, Location


class SubscriberForm(autocomplete.FutureModelForm):
    email = forms.CharField(initial='Your email ...')
    location = forms.ModelChoiceField(
            required=True,
            queryset=Location.objects.all(),
            widget=autocomplete.ModelSelect2(
                url='location-autocomplete',
                attrs={
                    'data-placeholder': 'Start typing your city ...',
                }
            )
    )

    class Meta:
        model = Subscriber
        fields = ('email', 'location')
