from dataclasses import field
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import User

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        field = ['username', 'email', 'password1', 'password2', 'avatar']