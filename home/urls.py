# home/urls.py

from django.conf import settings
from django.conf.urls.static import static
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
    path('dashboard/<int:user_id>/', dashboard, name='user_dashboard'),
    path('dashboard/<str:username>/', dashboard, name='user_dashboard_by_username'),
    path('follow/<int:user_id>/<int:action>/', follow, name='follow'),
    path('maps/', maps, name='maps'),
    path('create_post/', create_post, name='create_post'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('like/<uuid:post_id>/', like, name='like'),
    path('chats/', inbox, name='message'),
   	path('chats/direct/<username>', Directs, name='directs'),
   	path('chats/new/', UserSearch, name='search-users'),
   	path('chats/new/<username>', NewConversation, name='conversation'),
   	path('chats/send/', SendDirect, name='send-directs'),
    path('notifications/', ShowNOtifications, name='show-notifications'),
   	path('notifications/<noti_id>/delete', DeleteNotification, name='delete-notification'),
    # path('conversation/<int:user_id>/', conversation, name='conversation'),
    # path('<username>/', UserProfile, name='profile'),
    # path('<username>/saved/', UserProfile, name='profilefavourite'),
    # path('<username>/follow/<option>/', follow, name='follow'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
