from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from json import dumps as jdumps

from django.contrib.auth.decorators import login_required

from django.contrib import messages

# Create your views here.

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(request, "Account was created for " +user)
                return redirect('login')
            
            else:


                context = {"form":form}
                

                return render(request, "account_creator/register.html", context)

            

        form = RegisterForm()

        context = { "form":form}

        return render(request, "account_creator/register.html", context)


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    else:

        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "Username OR password is incorrect!")

        context = {}
        return render(request, "account_creator/login.html", context)


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url = 'login')
def home(request):
    return render(request, "account_creator/home.html")
