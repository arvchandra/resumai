from datetime import datetime, timedelta
import requests

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse

GOOGLE_USER_INFO_API_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        google_access_token = request.data.get("googleAccessToken")
        if not google_access_token:
            return Response({"error": "Access token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve Google user info using the provided access token
            resp = requests.get(
                GOOGLE_USER_INFO_API_URL,
                params={"access_token": google_access_token}
            )
            if resp.status_code != 200:
                raise Exception("Failed to fetch user info from Google")
            
            google_id_info = resp.json()

            email = google_id_info["email"]
            first_name = google_id_info.get("given_name", "")
            last_name = google_id_info.get("family_name", "")

            # Retrieve Django user using the Google email address.
            # Create new user if this is the user's first login.
            user, _ = User.objects.get_or_create(email=email, defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name
            })

            # Generate a refresh token (JSON Web Token)
            # and access token.
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            # Generate a response containing the access token and user details
            response = Response({
                "accessToken": access_token,
                "userInfo": {
                    "id": user.id,
                    "email": user.email,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                }
            })

            # The refresh token, set in an HTTPOnly cookie, can be used to obtain 
            # new access tokens without re-authenticating the user.
            response.set_cookie(
                key="refreshToken",
                value=refresh_token,
                httponly=True,
                secure=False,  # TODO: Change this to true for Production (Only over HTTPS)
                samesite="Lax",  # or "Strict"
                expires=datetime.now() + timedelta(days=7),
                path="/",  # Cookie can be access by any endpoint
            )
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refreshToken")
        if refresh_token is None:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token_object = RefreshToken(refresh_token)
            user_id = refresh_token_object["user_id"]
            user = User.objects.get(id=user_id)

            # Rotate/generate refresh token (JSON Web Token)
            # and access token.
            new_refresh = RefreshToken.for_user(user)
            new_refresh_token = str(new_refresh)
            new_access_token = str(new_refresh.access_token)

            # Generate a response containing the new access token and user details
            response = Response({
                "accessToken": new_access_token,
                "userInfo": {
                    "id": user.id,
                    "email": user.email,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                }
            })

            # The refresh token, set in an HTTPOnly cookie, can be used to obtain 
            # new access tokens without re-authenticating the user.
            response.set_cookie(
                key="refreshToken",
                value=new_refresh_token,
                httponly=True,
                secure=False,  # TODO: Change this to true for Production (Only over HTTPS)
                samesite="Lax",  # or "Strict"
                expires=datetime.now() + timedelta(days=7),
                path="/",  # Cookie can be access by any endpoint
            )
            return response

        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = JsonResponse({"message": "Logged out"})
        response.delete_cookie(
            "refreshToken", 
            path="/",
        )
        return response
