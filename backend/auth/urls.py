from django.urls import path

from .views import GoogleLoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path(
        "google-login/", 
        GoogleLoginView.as_view(), 
        name="google-login"
    ),
    path(
        "token/refresh/",
        RefreshTokenView.as_view(),
        name="refresh-token"
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),
]
