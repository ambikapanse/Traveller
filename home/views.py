from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import *
from django.contrib.auth.decorators import login_required


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


