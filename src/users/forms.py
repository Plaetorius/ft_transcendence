from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Friendship

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already in use")
        return username

    def save(self, commit=True):
        user = super().save(commit=False) # super() accesses the parent class
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username'].lower()
        if commit:
            user.save()
        return user

class UserSettingsForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'bio', 'profile_picture' ,'email')
