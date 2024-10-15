from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('map/', MapAPIView.as_view(), name='map'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetRequestDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetRequestConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetRequestCompleteView.as_view(), name='password_reset_complete'),
]