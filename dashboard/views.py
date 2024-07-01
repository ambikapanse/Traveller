from django.shortcuts import render
from django.http import HttpResponse



def user_logout(request):
    logout(request)
    return redirect('home:user_login')

def dashboard(request):
    return render(request, "dashboard.html")