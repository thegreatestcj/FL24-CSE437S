from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Profile
from datetime import date

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
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'New password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={
            'class': 'input w-full px-2 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-500',
            'placeholder': 'Confirm new password',
        })
    )

class ProfileUpdateForm(forms.ModelForm):
    # Include username and email from User model, set as disabled
    username = forms.CharField(
        max_length=150,
        disabled=True,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
            'placeholder': 'Enter username',
            'disabled': 'disabled'
        })
    )
    email = forms.EmailField(
        disabled=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
            'placeholder': 'Email address',
            'disabled': 'disabled'
        })
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full bg-gray-100 px-4 py-2 rounded-md'
        })
    )

    class Meta:
        model = Profile
        fields = ['alias', 'bio', 'location', 'birth_date', 'profile_image']
        widgets = {
            'alias': forms.TextInput(attrs={
                'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
                'placeholder': 'Display name (Alias)'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
                'placeholder': 'Tell us about yourself...',
                'rows': 3
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
                'placeholder': 'Enter your location'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full bg-gray-100 px-4 py-2 rounded-md',
                'type': 'date',
                'max': date.today().isoformat()
            }),
        }

    def __init__(self, *args, **kwargs):
        # Accept the user instance to initialize User fields
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set initial values for User fields
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

        # Ensure Profile fields are displayed even if they’re empty
            self.fields['alias'].initial = self.instance.alias or ''
            self.fields['bio'].initial = self.instance.bio or ''
            self.fields['location'].initial = self.instance.location or ''
            self.fields['birth_date'].initial = self.instance.birth_date or ''

    # def save(self, commit=True):
    #     # Save User fields first
    #     if self.user:
    #         self.user.username = self.cleaned_data.get('username', self.user.username)
    #         self.user.email = self.cleaned_data.get('email', self.user.email)
    #         self.user.save()

    #     # Save Profile fields
    #     profile = super().save(commit=False)
    #     if commit:
    #         profile.save()
    #     return profile
    def clean(self):
        cleaned_data = super().clean()
        alias = cleaned_data.get("alias")
        bio = cleaned_data.get("bio")
        location = cleaned_data.get("location")
        birth_date = cleaned_data.get("birth_date")
        profile_image = cleaned_data.get("profile_image")

        # Custom validation: Require at least one field to be filled
        if not (alias or bio or location or birth_date or profile_image):
            raise ValidationError("Please fill in at least one field.")

        return cleaned_data

class PasswordChangeRequestForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 mb-4 bg-gray-100 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Current Password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 mb-4 bg-gray-100 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 mb-4 bg-gray-100 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirm New Password'
        })
    )