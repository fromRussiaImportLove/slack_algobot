from django.urls import path
from .views import onInteractive, Event

urlpatterns = [
    path('dialog/', onInteractive.as_view(), name='interactiv_url'),
    path('start/', Event.as_view(), name='event_url'),
]
