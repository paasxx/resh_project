from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

def registerPage(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

        else:
            pass
            return HttpResponse("Dados inválidos")

        return redirect("home")

    else:
        form = RegisterForm()

    context = { "form":form}

    return render(response, "account_creator/register.html", context)


def loginPage(request):
    context = {}
    return render(request, "account_creator/login.html")

def home(request):
    return render(request, "account_creator/home.html")
