from django.urls import path, include
from .views import SendFile, onInteractiv, Register

urlpatterns = [
    path('getfile/', SendFile.as_view(), name='send_file_url'),
    path('dialog/', onInteractiv.as_view(), name='interactiv_url'),
    path('register/', Register.as_view(), name='register_url'),
]
