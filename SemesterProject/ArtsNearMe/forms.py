from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Confirm your password'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """
        A placeholder save method, where you would save the form data to your custom User model.
        Hash the password here before saving the User instance.
        """
        # Make sure you hash the password before saving the user to the database
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=make_password(self.cleaned_data['password'])  # Hash the password
        )
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Username'
        })
        
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Password'
        })
    )