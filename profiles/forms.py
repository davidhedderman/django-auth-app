from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ProfileUser


class ProfileUserCreationForm(UserCreationForm):


    class Meta:
        model = ProfileUser
        fields = ('username', 'email')


class ProfileUserChangeForm(UserChangeForm):


    class Meta:
        model = ProfileUser
        fields = UserChangeForm.Meta.fields
