from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

        else:
            pass
            return redirect("*")

        return redirect("home")

    else:
        form = RegisterForm()

    return render(response, "account_creator/register.html", {"form":form})

    

def home(request):
    return HttpResponse("Hello, welcome to your account creator!")
