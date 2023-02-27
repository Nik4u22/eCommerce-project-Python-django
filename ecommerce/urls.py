from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', user_home, name="user_home"),
    path('<slug>/' , get_product , name="get_product"),
]
