from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.models import Stream
from django.contrib.auth.models import User

try:
    from dashboard.models import Stream, Post
except ImportError:
    pass

@login_required
def home(request):
    user = request.user.id
    posts = Stream.objects.filter(user=user)
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    context = {
        'post_items': post_items,
    }
    print(post_items)
    return render(request, "index.html", context)

# Register view
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

#user_login
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

