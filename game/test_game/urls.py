from django.urls import path
from . import views

app_name = 'test_game'

urlpatterns = [
    path('', views.index, name='index')
]