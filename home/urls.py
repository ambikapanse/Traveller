# home/urls.py

from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),  # Add this line to handle the root URL
    path('home/', home, name='home'),
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('create_post/', create_post, name='create_post'),
    path('like/<uuid:post_id>/', like, name='like'),

]
