from django.shortcuts import render, redirect
from .forms import RegisterForm,ChangeEmailForm
from django.contrib.auth import  authenticate
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from rest_framework.authentication import get_authorization_header, TokenAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed,APIException
from .serializers import UserSerializer
from .authentication import create_access_token, create_refresh_token, decode_access_token
from rest_framework.settings import api_settings



import requests
import json
import requests



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
            
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                ### API connection ###
                r = requests.post('http://127.0.0.1:8000/api-login-user/', data={'username': username, 'password': password})
                
                if r.status_code == 200:
                    token = json.loads(r.content.decode("UTF-8")).get('token') 
                    request.session['token'] = token
                    request.session['username'] = username
                    
                    # redirect keeps the session data
                    #print(token)
                    response = redirect("home")
                
                    response.headers["Authorization"] =  "Bearer "+ token

                    return response
       
            else:
                messages.info(request, "Username OR password is incorrect!")

    context = {}
    return render(request, "account_creator/login.html", context)
        


def logoutPage(request):
    if request.session['token']!="":

        token = request.session['token']
        headers = {"Authorization": "Bearer "+ token }
        
        ### API connection ###
        r = requests.post('http://127.0.0.1:8000/api-logout-user/')


        if r.status_code == 200:
            request.session['token']=''
            return redirect("login")
        
    else:
        return redirect('login')
    


def updatePasswordPage(request):
    if request.session['token']!="":

        token = request.session['token']
        headers = {"Authorization": "Bearer "+ token }

        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES, headers = headers)
        data_user = response.json()
        userName = User.objects.filter(username=data_user['username']).first()


        if request.method == "POST":
                form = PasswordChangeForm(user =userName, data=request.POST)

                if form.is_valid():

                    if userName.check_password(form.cleaned_data['old_password']):
                        password = form.cleaned_data['new_password1']

                        ### API connection ###
                        r = requests.put('http://127.0.0.1:8000/api-update-password-user/',
                                        data={'old_password':form.cleaned_data['old_password'],
                                              'new_password1': password,
                                              'new_password2': password},
                                        headers = headers)
                        
                        if r.status_code == 200:
                    
                            messages.success(request, "Password updated!" )
                            return redirect('login')

                        
                    else:
                        messages.error(request, "Old password is Wrong!" )

                else:
                    
                    context = {"form":form}
                    return render(request, "account_creator/update.html", context)

        form = PasswordChangeForm(user= userName)
        context = {"form":form}
        return render(request, "account_creator/update.html", context)
    
    else:
        return redirect('login')



def updateEmailPage(request):
    if request.session['token']!="":

        token = request.session['token']
        headers = {"Authorization": "Bearer "+ token }

        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES, headers=headers)
        data_user = response.json()
        userName = User.objects.filter(username=data_user['username']).first()
        previous_email = userName.email

        print(userName,previous_email)

        if request.method == "POST":
                form = ChangeEmailForm( data=request.POST)
        
                if form.is_valid():
                    print("form e valido")
                    if form.cleaned_data['previous_email'] == previous_email:
                        new_email = form.cleaned_data['new_email']
                        print(token, headers)

                        ### API connection ###
                        r = requests.put("http://127.0.0.1:8000/api-update-email-user/",
                                         data={'previous_email': previous_email,'new_email': new_email}, 
                                         headers = headers
                                         )

                        if r.status_code == 200:
                    
                            messages.success(request, "Email was updated!" )
                            return redirect('login')
                        
                    else:
                        messages.error(request, "Previous email is wrong!" )
                
                else:
                    print("form n valido")
                    context = {"form":form}
                    return render(request, "account_creator/update_email.html", context)
        print("POST n valido")
        form = ChangeEmailForm()
        context = {"form":form}
        return render(request, "account_creator/update_email.html", context)
    
    else:
        
        return redirect('login')



def home(request):
    if request.session['token']!="":
   
        token = request.session['token']
        headers = {"Authorization": "Bearer "+ token }
        

        response = requests.get("http://127.0.0.1:8000/api-get-user/", cookies=request.COOKIES, headers = headers )
        data = response.json()
        return render(request, "account_creator/home.html", {'data':data})
    
    else:
        return redirect('login')


def deletePage(request):
    if request.session['token']!="":

        token = request.session['token']
        headers = {"Authorization": "Bearer "+ token }
        
        if request.method == "POST":
                form = AuthenticationForm(data=request.POST)

                if form.is_valid():

                    username = request.POST.get('username')
                    password = request.POST.get('password')
                    user = authenticate(request, username=username, password=password)

                    if user:

                            ### API connection ###
                            r = requests.delete('http://127.0.0.1:8000/api-delete-user/', headers = headers)

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
        user_data = request.data
        user_serializer = UserSerializer(data=user_data)
      
        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()
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
        auth = get_authorization_header(request).split()
        

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')

            id = decode_access_token(token)
            user = User.objects.filter(pk=id).first()

            return Response(UserSerializer(user).data)

        raise AuthenticationFailed('Unauthenticated')
    
    
class UpdatePasswordUserView(APIView):
    def put(self, request):

        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')

            if not token:
                raise AuthenticationFailed('Unauthenticated!')
            
            id = decode_access_token(token)
            user_object = User.objects.get(id=id)

            data = request.data

            user_object.password = make_password(data["new_password1"])
            user_object.save()
            serializer = UserSerializer(user_object)
            return Response(serializer.data)


class UpdateEmailUserView(APIView):
    def put(self, request):
        auth = get_authorization_header(request).split()
        
        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')

            if not token:
                raise AuthenticationFailed('Unauthenticated!')
        
            id = decode_access_token(token)
            user_object = User.objects.get(id=id)
            data = request.data
            user_object.email = (data["new_email"])
            user_object.save()
            serializer = UserSerializer(user_object)
            return Response(serializer.data)
    
    
        
class LogoutView(APIView):
    def post(self, request):
        
        response = Response()
        
        response.data = {
            "message": "success"
        }
        return response
    

class DeleteUserView(APIView):
    def delete(self, request):

        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            id = decode_access_token(token)
            user = User.objects.filter(pk=id).first()
            user.delete()
            return Response({"result":"user deleted"})
        
        else:
            raise AuthenticationFailed('Unauthenticated!')
    
