from django.urls import path

from whether import views
from whether.utils.cities import load_cities

# This is in here because urls is loaded exactly once on server startup
load_cities()

urlpatterns = [
    path('<int:pk>/update/', views.UpdateView.as_view(), name='update'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('success/<int:subscriber_id>', views.success, name='success'),
    path('location-autocomplete/', views.LocationAutocomplete.as_view(), name='location-autocomplete')
]
