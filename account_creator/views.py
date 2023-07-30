from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm


from django.contrib import messages

# Create your views here.

def registerPage(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, "Account was created for " +user)
            return redirect('login')

    
    form = RegisterForm()

    context = { "form":form}

    return render(request, "account_creator/register.html", context)


def loginPage(request):

    if request.method == "POST":
        request.POST.get('useranme')
        request.POST.get('password')
    context = {}
    return render(request, "account_creator/login.html")

def home(request):
    return render(request, "account_creator/home.html")
