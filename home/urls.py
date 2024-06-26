# home/urls.py

from django.urls import path
from .views import home, user_login, user_register, user_logout  

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
]
