from django.urls import path

from .views import GoogleLoginView, RefreshTokenView

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
]
