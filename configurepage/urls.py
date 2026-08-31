from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('direct/', home, name='home'),
]