# home/urls.py

from django.urls import path
from .views import home, user_login, user_register, user_logout  

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),  # Add this line to handle the root URL
    path('home/', home, name='home'),
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
]
