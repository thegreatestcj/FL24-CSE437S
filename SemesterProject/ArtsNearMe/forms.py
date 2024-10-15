from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Fields from the User model
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Email'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
                'placeholder': 'Password'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error("email", "This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error("username", "This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash the password before saving the user
        user.password = make_password(self.cleaned_data['password'])
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

class PasswordResetRequestForm(PasswordResetForm):
    email = forms.EmailField(
    widget=forms.EmailInput(attrs={
        'class': 'input w-full px-2 py-2 mb-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
        'placeholder': 'Email'
    })
)

class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'New password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm new password',
        })
    )