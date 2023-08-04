from django.shortcuts import render, redirect
from .forms import RegisterForm,UpdateForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserChangeForm,PasswordChangeForm
from django.contrib.auth.models import User
from rest_framework import exceptions

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.authentication import get_authorization_header,TokenAuthentication,SessionAuthentication,BasicAuthentication


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed,APIException
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .authentication import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token

import requests

import json

import requests
import base64



# Create your views here.

def registerPage(request):

    if request.method == "POST":
            form = RegisterForm(request.POST)

            username = request.POST.get('username')
            password = request.POST.get('password1')
            email = request.POST.get('email')

            if form.is_valid():

                ### API connection ###
                r = requests.post('http://127.0.0.1:8000/api-create-user/', 
                                  data={
                                      'username': username, 
                                      'email': email,
                                      'password': password})

                if r.status_code == 200:
                    response = r.json()
                    messages.success(request, "Account was created for " + username)
                    print("Redirecting to Login")
                    return redirect('login')
            
            else:
                context = {"form":form}
                return render(request, "account_creator/register.html", context)

    form = RegisterForm()
    context = {"form":form}
    return render(request, "account_creator/register.html", context)
        


def loginPage(request):

    if request.method == "POST":
            print("Posted login data")
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                ### API connection ###
                r = requests.post('http://127.0.0.1:8000/api-login-user/', data={'username': username, 'password': password})

                if r.status_code == 200:
                    # PEGA O TOKEN DA RESPOSTA DE 'api-login-user' 
                    token = json.loads(r.content.decode("UTF-8")).get('token')
                    # COLOCA O TOKEN NA SESSÃO 
                    request.session['token'] = token
                    # redirect keeps the session data
                    print("redirecting home")
                    return redirect("home")
       
            else:
                messages.info(request, "Username OR password is incorrect!")

    context = {}
    return render(request, "account_creator/login.html", context)
        


def logoutPage(request):

    ### API connection ###
    r = requests.post('http://127.0.0.1:8000/api-logout-user/')
    response = r.json()

    if r.status_code == 200:
        return redirect("login")
    


def updatePage(request):


    response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES)
    data_user = response.json()
    userName = User.objects.filter(username=data_user['username']).first()


    if request.method == "POST":
            form = PasswordChangeForm(user =userName, data=request.POST)
    
            if form.is_valid():

                print("O form é validoo")

                password = form.cleaned_data['new_password1']


                ### API connection ###
                r = requests.put('http://127.0.0.1:8000/api-update-user/', cookies=request.COOKIES,
                                  data={ 
                                      
                                      'password': password})

                if r.status_code == 200:
                    # PEGA O TOKEN DA RESPOSTA DE 'api-login-user' 
                    token = json.loads(r.content.decode("UTF-8")).get('token')
                    # COLOCA O TOKEN NA SESSÃO bruno
                    request.session['token'] = token
                    # redirect keeps the session data

                    messages.success(request, "Account was updated for " )
                    print("Redirecting to Login")
                    return redirect('login')
            
            else:
                print(form.errors)
                print("O form n é validoo")
                context = {"form":form}
                return render(request, "account_creator/update.html", context)


    form = PasswordChangeForm(userName)
    context = {"form":form}
    return render(request, "account_creator/update.html", context)




def home(request):
    print("Trying to Access api")

    response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES)
    data = response.json()
    print(data)
    return render(request, "account_creator/home.html", {'data':data})



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

    def post(self, request):
        user = User.objects.filter(username=request.data['username']).first()
        

        if not user:
            raise APIException("User not found!")
        
        if not user.check_password(request.data['password']):
            raise APIException("User not found!")
           
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()

        response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token
        }

        return response
    


class UserView(APIView):
    
    def get(self, request):
        # NÃO É NECESSÁRIO UTILIZAR A FUNÇÃO QUE ESTAVA ANTERIORMENTE, BASTA PEGAR O TOKEN DA SESSÃO. bruno
        auth = request.session['token']

        if auth:
            # PODE SER PASSADO DIRETO PARA ESSE DECODE. bruno
            id = decode_access_token(auth)

            user = User.objects.filter(pk=id).first()

            return Response(UserSerializer(user).data)

        raise AuthenticationFailed('Unauthenticated')
    
    
class UpdateUserView(APIView):
    def put(self, request):

        token = request.session['token']

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        id = decode_access_token(token)
        
        user_object = User.objects.get(id=id)

        data = request.data

        #user_object.email = data["email"]
        user_object.password = data["password"]
      
        user_object.save()

        serializer = UserSerializer(user_object)
        return Response(serializer.data)
    
    
        


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message": "success"
        }
        return response
    
# class HomeView(APIView):
#     response = Response()
#     return response