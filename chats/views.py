from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template 

from chats.models import Message
# Create your views here.

@login_required
def chats(request):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, recipient=message['user'])
        directs.update(is_read = True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
        
        context = {
            'directs': directs,
            'messages': messages,
            'active_direct': active_direct
        }


    return render(request, 'chats.html', context)