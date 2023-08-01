from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from .serializers import UserSerializer

import jwt,datetime, requests




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
        context = {"form":form}
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

class RegisterView(APIView):
    def post(self, request, format=None):
        print("Creating a user")
        user_data = request.data
        user_serializer = UserSerializer(data=user_data)
      
        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()
            print("User created")
            return Response({"user":user_serializer.data}, status=200)
        
        return Response({"msg":"ERR"}, status=400)
    

    
class LoginView(APIView):
    
    def post(self, request, format=None):
        user_password = User.objects.filter(password=request.data['password']).first()
        user_username = User.objects.filter(username=request.data['username']).first()
        user_obj = user_password or user_username

        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': request.data['password'] 
            }
            user = authenticate(**credentials)

            if user and user.is_active:

                payload ={
                    'id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                    'iat': datetime.datetime.utcnow()
                }

                token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
                response = Response()
                response.set_cookie(key='jwt', value=token, httponly=True)

                response.data = {
                    'jwt': token
                }
                
                return render(request, "account_creator/login.html", context=response.data)
                #return response
            
        
        raise AuthenticationFailed("User not found!")

class UserView(APIView):
    def get(self, request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message": "success"
        }
        return response