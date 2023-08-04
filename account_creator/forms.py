from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class RemoveUser(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User

class ChangeEmailForm(forms.Form):
    
    previous_email= forms.CharField(widget=forms.EmailInput)
    new_email = forms.CharField(widget=forms.EmailInput)

    class Meta:
        model = User