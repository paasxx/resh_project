from django.shortcuts import render, redirect
from .forms import RegisterForm,UpdateForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from .serializers import UserSerializer

import jwt,datetime, requests




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
                    response = r.json()
                    token = response['jwt']
                                 
                    # Save token to session
                    request.session['api_token'] = token
                    request.session['user'] = username

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

    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username,password)

    if request.method == "POST":
            
            print("Lets Change")
            form = UpdateForm(instance=username)

    
            password = request.POST.get('password')
            email = request.POST.get('email')
            print(password,email)

            if form.is_valid():

                ### API connection ###
                r = requests.post('http://127.0.0.1:8000/api-update-user/', 
                                  data={ 
                                      'email': email,
                                      'password': password})

                if r.status_code == 200:
                    response = r.json()
                    messages.success(request, "Account was updated for " )
                    print("Redirecting to Login")
                    return redirect('login')
            
            else:
                context = {"form":form}
                return render(request, "account_creator/home.html", context)

    form = UpdateForm(instance = username)
    context = {"form":form}
    return render(request, "account_creator/home.html", context)




def home(request):
    response = requests.get("http://127.0.0.1:8000/api-get-user/")
    data = response.json()
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
                    'jwt': token,
                    'username': user_obj.username
                }
                return response
            
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
    
class UpdateUserView(APIView):
    def put(self, request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        id = request.query_params["id"]
        user_object = User.objects.get(id=id)

        data = request.data

        user_object.email = data["email"]
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