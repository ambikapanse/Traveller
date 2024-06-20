from django.shortcuts import render
from django.http import HttpResponse


def livestreams(request):
    return render(request, "livestreams.html")
