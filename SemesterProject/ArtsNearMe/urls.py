from django.contrib import admin
from django.urls import path, include
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='home'),
    path('map/api/', MapAPIView.as_view(), name='map_api'),
    path('map/', get_map, name='map'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetRequestDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetRequestConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetRequestCompleteView.as_view(), name='password_reset_complete'),
        # Place endpoints
    path('map/api/favorite/place/add/', add_favorite_place, name='add_favorite_place'),
    path('map/api/favorite/place/remove/', remove_favorite_place, name='remove_favorite_place'),
    path('map/api/favorites/places/', list_favorite_places, name='list_favorite_places'),

    # Event endpoints
    path('map/api/favorite/event/add/', add_favorite_event, name='add_favorite_event'),
    path('map/api/favorite/event/remove/', remove_favorite_event, name='remove_favorite_event'),
    path('map/api/favorites/events/', list_favorite_events, name='list_favorite_events'),

    # Inside profile
    path('profile/update/', update_profile, name='update_profile'),
    path('profile/favorite-places/', favorite_places, name='favorite_places'),
    path('profile/favorite-events/', favorite_events, name='favorite_events'),

    # User settings
    path('profile/settings/', redirect_to_change_password, name='settings'),  # Redirects to change password
    path('profile/settings/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/settings/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
]
