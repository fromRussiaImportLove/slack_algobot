from django.urls import path, include
from .views import GetTest, GetHint, onInteractiv, Register, Event

urlpatterns = [
    path('gettest/', GetTest.as_view(), name='get_test_url'),
    path('gethint/', GetHint.as_view(), name='get_task_url'),    
    path('dialog/', onInteractiv.as_view(), name='interactiv_url'),
    path('register/', Register.as_view(), name='register_url'),
    path('start/', Event.as_view(), name='event_url'),
]