from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User



from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer



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


# def changePassword(request):



@login_required(login_url = 'login')
def home(request):

    form = UserChangeForm(instance=request.user)
    context= {"form":form}
    return render(request, "account_creator/home.html", context)



## API Functions

class UserView(APIView):


    def post(self, request, format=None):
        print("Creating a user")

        user_data = request.data

        user_serializer = UserSerializer(data=user_data)
      
        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()
            print("User created")
            return Response({"user":user_serializer.data}, status=200)
        
        return Response({"msg":"ERR"}, status=400)
    

    
class UserLoginView(APIView):

     #Convert a user token into user data
    
    def get(self, request, format=None):

        if request.user.is_authenticated == False or request.user.is_active == False:
            return Response("Invalid Credentials", status=403)
        
        user = UserSerializer(request.user)
        return Response(user.data, status=200)
    
    def post(self, request, format=None):

        user_obj = User.objects.filter(password=request.data['password']).first() or User.objects.filter(username=request.data['username']).first()

        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': request.data['password']

            }
            user = authenticate(**credentials)

            if user and user.is_active:
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=200)
        
        return Response("Invalid Credentials", status=403)
    