from django.urls import path, include
from .views import GetFile, onInteractiv, Register, Event

urlpatterns = [
    path('getfile/', GetFile.as_view(), name='get_file_url'),
    path('dialog/', onInteractiv.as_view(), name='interactiv_url'),
    path('register/', Register.as_view(), name='register_url'),
    path('start/', Event.as_view(), name='event_url'),
]
