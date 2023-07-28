from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

# Create your views here.

class HomePageView(TemplateView):
    template_name = "account_creator/home.html"

def home(request):
    return HttpResponse("Hello, welcome to your account creator!")
