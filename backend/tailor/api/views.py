import os

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

from tailor.api.serializers import FileUploadSerializer, ResumeSerializer
from tailor.models import Resume


class ParseJobPostingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        linkedin_job_id = request.query_params.get("linkedInJobID")
        if not linkedin_job_id:
            raise ValidationError(
                {"linkedInJobID": "This query parameter is required."}
            )

        job_description_text = f'The LinkedIn job ID for this request is: {linkedin_job_id}'

        return Response(
            {"jobDescriptionText": job_description_text},
            status.HTTP_200_OK,
        )


class UserResumeListView(ListAPIView):
    serializer_class = ResumeSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Resume.objects.filter(user__id=user_id)


class UserResumeUploadView(APIView):
    """
    API endpoint to handle resume uploads for a specific user

    Accepts a POST request with a single file in the 'file' field of the payload.
    Validated and processes the uploaded file. Responds with the saved file name
    if the upload was successful.

    Example request:
        POST /tailor/user/<int:user_id>/resume/upload/
        Content-Type: multipart/form-data
        Body:
            file: <uploaded_file>

    Responses:
        200 OK: {"filename": "<uploaded_file_name>"}
        400 Bad Request: {"file": ["This field is required."]}
    """
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            user_id = self.kwargs["user_id"]
            uploaded_file = serializer.validated_data["file"]

            # Get the file extension
            _, extension = os.path.splitext(uploaded_file.name)  # includes the dot (e.g., '.jpg')

            # Save the file via the Resume model
            new_resume_upload = Resume()
            new_resume_upload.name = uploaded_file.name
            new_resume_upload.file = uploaded_file
            new_resume_upload.file_type = str(extension).upper()
            new_resume_upload.user = User.objects.get(id=user_id) # TODO: Get user from auth
            new_resume_upload.save()

            return Response(
                {"user_id": user_id},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
