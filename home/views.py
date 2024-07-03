from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from dashboard.models import *
from dashboard.models import Like
from django.http import HttpResponseRedirect

# def maplocations(request):

#Profile picture
@login_required
def pfp(request):
    user = request.user
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    profile = user.profile
    return render(request, 'base.html', {'profile':profile})

# DASHBOARD
@login_required
def dashboard(request):
    user = request.user
    # Ensure user has a profile
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    profile = user.profile  # Get the profile associated with the logged-in user

    # Fetch the posts for the logged-in user
    post_items = Post.objects.filter(user=user)
    print(f"User ID: {user.id}")  # Debugging line
    print(f"Post Items: {post_items}")  # Debugging line

    #edit profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('home:dashboard') # Redirect to dashboard or another page upon successful form submission
    else:
        form = ProfileForm(instance=request.user.profile)  # Create form for current user's profile data
    
    
    context = {
        'profile': profile,
        'post_items': post_items,
        'form':form
    }
    return render(request, 'dashboard.html', context)

# new post
def create_post(request):
    user = request.user
    if request.method=='POST':
        postform = PostForm(request.POST, request.FILES)
        if postform.is_valid():
            picture = postform.cleaned_data.get('picture')
            caption = postform.cleaned_data.get('caption')
            location = postform.cleaned_data.get('location')

            p, created = Post.objects.get_or_create(picture=picture, caption=caption, location=location, user=user)
            p.save()
            return redirect('home:dashboard')
    else:
        postform = PostForm()
    
    context = {
        'form' : postform
    }
    return render(request, 'post.html', context)

@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes

    liked = Like.objects.filter(user=user, post=post).count()
    if not liked:
        like = Like.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Like.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
    
    post.likes = current_likes
    post.save()
    
    return HttpResponseRedirect(reverse('home:index'))

    
# HOME PAGE
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

