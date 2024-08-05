from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from dashboard.models import *
from django.http import JsonResponse, HttpResponseNotFound
from django.core.files.storage import default_storage
import json
import requests
from django.template.loader import get_template 
from chats.models import Message
from django.core.paginator import Paginator
from django.db.models import Q

from bs4 import BeautifulSoup
import random

from uuid import UUID

#follow
@login_required
def follow(request, user_id, action):
    user_to_follow = get_object_or_404(User, id=user_id)
    current_user = request.user

    if action == 1:
        # Follow the user
        if current_user != user_to_follow:
            follow, created = Follow.objects.get_or_create(follower=current_user, following=user_to_follow)
            messages.success(request, f'You are now following {user_to_follow.username}.')
            if created:
                # Add all posts of the followed user to the follower's stream
                posts = Post.objects.filter(user=user_to_follow)
                for post in posts:
                    Stream.objects.get_or_create(
                        post=post,
                        user=current_user,
                        date=post.posted,
                        following=user_to_follow
                    )

        
    elif action == 0:
        # Unfollow the user
        follow_instance = Follow.objects.filter(follower=current_user, following=user_to_follow).first()
        if follow_instance:
            follow_instance.delete()
            Stream.objects.filter(user=current_user, following=user_to_follow).delete()

            messages.success(request, f'You have unfollowed {user_to_follow.username}.')
        else:
            messages.error(request, 'You are not following this user.')

    return redirect(request.META.get('HTTP_REFERER', 'home:dashboard'))  # Redirect back to the previous page or dashboard

#webscraping

def fetch_article():
    url = 'https://www.lonelyplanet.com/articles'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article')
    if(articles):
        n = random.randint(0, len(articles)-1)
        article = articles[n]
            # Extract article details
        img_tag = article.find('img')
        img_url = img_tag['src'] if img_tag else None
        title_tag = article.find('a')
        title = title_tag.text.strip() if title_tag else None
        rel_url = title_tag['href'] if title_tag else None
        description_tag = article.find('p', class_='text-sm')
        description = description_tag.text.strip() if description_tag else None
        base_url = 'https://www.lonelyplanet.com'
        link = base_url+rel_url

    return title, link, img_url, description


# notifications
def ShowNOtifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

    title, link, img_url, description = fetch_article()
    article = {
        'title': title,
        'link': link,
        'img_url': img_url,
        'description': description
    }
    
    context = {
        'notifications': notifications,
        'article': article  # Added article to context if needed
    }
    
    return render(request, 'notifications.html', context)


def DeleteNotification(request, noti_id):
	user = request.user
	Notification.objects.filter(id=noti_id, user=user).delete()
	return redirect('home:show-notifications')


def CountNotifications(request):
	count_notifications = 0
	if request.user.is_authenticated:
		count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()

	return {'count_notifications':count_notifications}
	


#messages
@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'directs':directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile': profile,
    }
    return render(request, 'chats.html', context)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)

    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }
    return render(request, 'chats.html', context)

def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.sender_message(from_user, to_user, body)
        return redirect('home:message')

def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
            }

    return render(request, 'search_users.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('home:search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
    return redirect('home:message')

#maps
@login_required
def maps(request):
    user = request.user
    followings = Follow.objects.filter(follower=user).select_related('following')
    following_list = []
    locations = []
    for follow in followings:
        user_followed = Profile.objects.get(user=follow.following)
        following_list.append(user_followed)
        
        response = requests.get("https://nominatim.openstreetmap.org/search?format=json&limit=1&q='"+ user_followed.location)
        if response.status_code == 200:

            data = response.json()

            if(data):
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                tag = str(user_followed.user)
                locations.append([lat,lon,tag])
        else:
            print("No data received")

    context = {
        'following_list': following_list,
        'locations': json.dumps(locations)
    }
    return render(request, 'maps.html', context)

# DASHBOARD
@login_required
def dashboard(request, user_id=None):
    if user_id is None:
        user = request.user
    else:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found")
        # Ensure user has a profile
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    profile = user.profile  # Get the profile associated with the logged-in user

    followers = Follow.objects.filter(following=user)
    followings = Follow.objects.filter(follower=user)

    post_items = Post.objects.filter(user=user)
    liked_posts = Likes.objects.filter(user=user).values_list('post_id', flat=True)
    post_items_with_likes = [
        {
            'post': post,
            'liked': post.id in liked_posts
        }
        for post in post_items
    ]

    # Set profile variables
    profile.followers_count = followers.count()
    profile.following_count = followings.count()
    profile.places_travelled = post_items.count()
    profile.save()

    follow_status = Follow.objects.filter(follower=request.user, following=profile.user).exists()

    print(f"User ID: {user.id}")  # Debugging line
    print(f"followings: {followings.count()}")  # Debugging line

    #edit profile
    if request.method == 'POST' and user_id is None:
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('home:dashboard') # Redirect to dashboard or another page upon successful form submission
    else:
        form = ProfileForm(instance=request.user.profile)  # Create form for current user's profile data
    
    
    context = {
        'profile': profile,
        'post_items_with_likes': post_items_with_likes,
        'form':form,
        'follow_status':follow_status
    }
    return render(request, 'dashboard.html', context)

# new post
def create_post(request):
    user = request.user
    if request.method == 'POST':
        postform = PostForm(request.POST, request.FILES)
        if postform.is_valid():
            picture = postform.cleaned_data.get('picture')
            caption = postform.cleaned_data.get('caption')
            location = postform.cleaned_data.get('location')

            # Create or get the post
            post, created = Post.objects.get_or_create(picture=picture, caption=caption, location=location, user=user)
            
            if created:
                # If the post was newly created, add it to the stream for users following the author
                followers = Follow.objects.filter(following=user)
                for follower in followers:
                    Stream.objects.get_or_create(
                        post=post,
                        user=follower.follower,
                        date=post.posted,
                        following=user
                    )
            post.save()
            return redirect('home:dashboard')
    else:
        postform = PostForm()

    context = {
        'form': postform
    }
    return render(request, 'post.html', context)

#edit profile
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                print(f"Profile picture: {profile.profile_picture}")  # Debugging line
                print(f"File path: {default_storage.save(profile.profile_picture.name, request.FILES['profile_picture'])}")  # Debugging line
            profile.save()
            return redirect('home:dashboard')  # Redirect to dashboard or another page upon successful form submission
    else:
        form = ProfileForm(instance=request.user.profile)  # Create form for current user's profile data

    #     if form.is_valid():
    #         form.save()
    #         return redirect('home:dashboard') # Redirect to dashboard or another page upon successful form submission
    # else:
    #     form = ProfileForm(instance=request.user.profile)  # Create form for current user's profile data

    
    context = {
        'form':form
    }
    return render(request, 'edit_prf.html', context)
    
@login_required
def like(request, post_id):
    user = request.user
    try:
        post_id = UUID(str(post_id))  # Ensure post_id is a UUID
        post = get_object_or_404(Post, id=post_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid post ID'}, status=400)

    liked = Likes.objects.filter(user=user, post=post).exists()

 
    if not liked:
        Likes.objects.create(user=user, post=post)
        post.likes = post.likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        post.likes = post.likes - 1

    post.save()
    return JsonResponse({'likes': post.likes})

    
# HOME PAGE

@login_required
def home(request):
    user = request.user.id
    posts = Stream.objects.filter(user=user)
    print("posts to see: ", posts)
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    #Check liked status for each post
    liked_posts = Likes.objects.filter(user=user).values_list('post_id', flat=True)
    post_items_with_likes = [
        {
            'post': post,
            'liked': post.id in liked_posts
        }
        for post in post_items
    ]

    
    followings = Follow.objects.filter(follower=user).select_related('following')
    following_list = []
    for follow in followings:
        user_followed = Profile.objects.get(user=follow.following)
        following_list.append(user_followed)

    #what's new
    title, link, img_url, description = fetch_article()
    article = {'title':title, 
               'link':link, 
               'img_url':img_url, 
               'description':description}

    context = {
        'post_items_with_likes': post_items_with_likes,
        'following_list': following_list,
        'article':article
    }
    # print(post_items)
    return render(request, "index.html", context)




# REGISTER VIEW
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            login(request, user)
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('home:user_login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# LOGIN VIEW
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home:home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home:user_login')

