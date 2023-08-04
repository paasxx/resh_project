from django.shortcuts import render, redirect
from .forms import RegisterForm,ChangeEmailForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,UserChangeForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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
                    request.session['username'] = username
                    # redirect keeps the session data
                    print("redirecting home")
                    return redirect("home")
       
            else:
                messages.info(request, "Username OR password is incorrect!")

    context = {}
    return render(request, "account_creator/login.html", context)
        


def logoutPage(request):

    if request.session['token']!="":

        ### API connection ###
        r = requests.post('http://127.0.0.1:8000/api-logout-user/', cookies=request.COOKIES)
        
        if r.status_code == 200:
            return redirect("login")
        
    else:

        return redirect('login')
    


def updatePasswordPage(request):

    if request.session['token']!="":

        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES)
        data_user = response.json()
        userName = User.objects.filter(username=data_user['username']).first()


        if request.method == "POST":
                form = PasswordChangeForm(user =userName, data=request.POST)
        
                if form.is_valid():

                    if userName.check_password(form.cleaned_data['old_password']):
                     

                        password = form.cleaned_data['new_password1']


                        ### API connection ###
                        r = requests.put('http://127.0.0.1:8000/api-update-password-user/', cookies=request.COOKIES,
                                        data={ 
                                            
                                            'password': password})

                       
                        messages.success(request, "Password updated!" )
                        print("Redirecting to Login")
                        return redirect('login')
                        
                    else:

                        messages.error(request, "Old password is Wrong!" )

                
                else:
                    
                    print("O form n é validoo")
                    context = {"form":form}
                    return render(request, "account_creator/update.html", context)


        form = PasswordChangeForm(user= userName)
        context = {"form":form}
        return render(request, "account_creator/update.html", context)
    
    else:

        return redirect('login')



def updateEmailPage(request):

    if request.session['token']!="":

        
        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES)
        data_user = response.json()
        userName = User.objects.filter(username=data_user['username']).first()
        previous_email = userName.email

        


        if request.method == "POST":
                form = ChangeEmailForm( data=request.POST)
        
                if form.is_valid():


                    if form.cleaned_data['previous_email'] == previous_email:

                        new_email = form.cleaned_data['new_email']

                        ### API connection ###
                        r = requests.put('http://127.0.0.1:8000/api-update-email-user/', cookies=request.COOKIES,
                                        data={ 
                                            
                                            'new_email': new_email})

                        if r.status_code == 200:
                            # PEGA O TOKEN DA RESPOSTA DE 'api-login-user' 
                            token = json.loads(r.content.decode("UTF-8")).get('token')
                            # COLOCA O TOKEN NA SESSÃO bruno
                            request.session['token'] = token
                            # redirect keeps the session data

                            messages.success(request, "Email was updated!" )
                            print("Redirecting to Login")
                            return redirect('login')
                        
                    else:
                        messages.error(request, "Previous email is wrong!" )
                
                else:
                    
                    print("O form n é validoo")
                    context = {"form":form}
                    return render(request, "account_creator/update_email.html", context)


        form = ChangeEmailForm()
        context = {"form":form}
        return render(request, "account_creator/update_email.html", context)
    
    else:

        return redirect('login')



def home(request):

    if request.session['token']!="":

        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES)
        data = response.json()
        return render(request, "account_creator/home.html", {'data':data})
    
    else:
        return redirect('login')



def deletePage(request):
   
    if request.session['token']!="":


        if request.method == "POST":
                form = AuthenticationForm(data=request.POST)

                if form.is_valid():

                    username = request.POST.get('username')
                    password = request.POST.get('password')

                    user = authenticate(request, username=username, password=password)

                    if user:

                            ### API connection ###
                            r = requests.delete('http://127.0.0.1:8000/api-delete-user/', cookies=request.COOKIES)

                            if r.status_code == 200:
                                messages.success(request, "Account was Deleted!" )
                                return redirect('register')
                    else:
                        messages.error(request, "Verify Username and Password" )
                
                else:
                    
                    context = {"form":form}
                    return render(request, "account_creator/delete.html", context)

        
        form = AuthenticationForm()
        context = {"form":form}
        return render(request, "account_creator/delete.html", context)
    
    else:

        return redirect('login')


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
    
    
class UpdatePasswordUserView(APIView):
    def put(self, request):

        token = request.session['token']

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        id = decode_access_token(token)

        user_object = User.objects.get(id=id)

        data = request.data

        #user_object.email = data["email"]
        user_object.password = make_password(data["password"])
      
        user_object.save()

        serializer = UserSerializer(user_object)
        return Response(serializer.data)
    
class UpdateEmailUserView(APIView):
    def put(self, request):

        token = request.session['token']

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        id = decode_access_token(token)

        user_object = User.objects.get(id=id)

        data = request.data
        print(data)

        #user_object.email = data["email"]
        user_object.email = (data["new_email"])
      
        user_object.save()

        serializer = UserSerializer(user_object)
        return Response(serializer.data)
    
    
        


class LogoutView(APIView):
    def post(self, request):
        
        response = Response()
        
        response.delete_cookie('token')
        request.session['token']=''
        response.data = {
            "message": "success"
        }
        return response
    
class DeleteUserView(APIView):

    def delete(self, request):

        auth = request.session['token']
        print(auth)

        if auth:
            # PODE SER PASSADO DIRETO PARA ESSE DECODE.
            id = decode_access_token(auth)

            user = User.objects.filter(pk=id).first()

            
            user.delete()

            return Response({"result":"user deleted"})
        
        else:
                  
            raise AuthenticationFailed('Unauthenticated!')
    
