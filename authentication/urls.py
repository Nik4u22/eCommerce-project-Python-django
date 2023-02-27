from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('user-home', user_home, name="user_home"),
    path('signup', signup, name='signup'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forget-password', forget_password, name='forget-password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset-password'),
]
