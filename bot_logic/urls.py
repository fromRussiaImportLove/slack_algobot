from django.urls import path

from .views import Event, Select, OnInteractive

urlpatterns = [
    path('dialog/', OnInteractive.as_view(), name='interactiv_url'),
    path('start/', Event.as_view(), name='event_url'),
    path('select/', Select.as_view(), name='select_url'),
]
