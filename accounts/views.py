from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse

# Create your views here.
def persona_login(request):
    user = authenticate(assertion=request.POST['assertion'])
    if user:
        login(request, user)
    return HttpResponse('OK')
