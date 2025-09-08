import os

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import FileResponse
from django.contrib.auth.models import User

from tailor.api.serializers import FileUploadSerializer, ResumeSerializer, TailoredResumeSerializer
from tailor.models import Resume, TailoredResume

from tailor.exceptions import ParsingError


class UserResumeListView(ListAPIView):
    serializer_class = ResumeSerializer

    def get_queryset(self):
        user = self.request.user
        return Resume.objects.filter(user=user)


class UserResumeUploadView(APIView):
    """
    API endpoint to handle resume uploads for a specific user

    Accepts a POST request with a single file in the 'file' field of the payload.
    Validated and processes the uploaded file. Responds with the saved file name
    if the upload was successful.

    Example request:
        POST /tailor/resume/upload/
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
            user = self.request.user
            uploaded_file = serializer.validated_data["file"]

            # Get the file type (uppercase file extension)
            _, extension = os.path.splitext(uploaded_file.name)
            file_type = str(extension[1:]).upper()  # excludes the dot (e.g., 'DOCX')

            # Save the file via the Resume model
            new_resume_upload = Resume()
            new_resume_upload.name = uploaded_file.name
            new_resume_upload.file = uploaded_file
            new_resume_upload.file_type = file_type
            new_resume_upload.user = User.objects.get(id=user.id)
            new_resume_upload.save()

            resume_serializer = ResumeSerializer(new_resume_upload)
            resume_json_data = {"uploadedResume": resume_serializer.data}
            
            return Response(
                resume_json_data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TailoredResumeListView(ListAPIView):
    serializer_class = TailoredResumeSerializer

    def get_queryset(self):
        user = self.request.user
        return TailoredResume.objects.filter(user=user).order_by('-created_at')


class TailoredResumeDownloadView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        tailored_resume_id = self.kwargs["tailored_resume_id"]

        try:
            tailored_resume = TailoredResume.objects.get(pk=tailored_resume_id, user=user)

            return FileResponse(tailored_resume.file.open(), 'rb', as_attachment=True)
        except TailoredResume.DoesNotExist:
            # TODO error handling; V1
            return Response(
                {
                    "error": "File is not accessible"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except TailoredResume.MultipleObjectsReturned:
            # TODO error handling; V1
            return Response(
                    {
                        "error": "Could not retrieve correct file"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        

class TailorResumeView(APIView):
    """
    API endpoint that performs the resume tailoring tasks.

    - Accepts a POST request with a payload containing a Resume ID and a Job Posting URL.
    - Sends the payload to TailoredResumeManager that uses it to fetch the resume and parses the job posting
    - Builds a prompt from the parsed resume text and job description, and sends
      the request to OpenAI API.
    - Creates the TailoredResume object using the parsed resume, job description, and OpenAI response.
    - Responds with the TailoredResume id if the process was successful.

    Example request:
        POST /tailor/tailor-resume
        Content-Type: application/json
        Body:
            {
                "resume_id": 123,
                "job_posting_url": "https://www.linkedin.com/jobs/view/4117993213"
            }

    Responses:
        201 Created
        400 Bad Request
    """

    def post(self, request, *args, **kwargs):
        user = self.request.user
        resume_id: int = int(request.data["resume_id"])
        job_posting_url: str = request.data["job_posting_url"]

        try:
            tailored_resume = TailoredResume.objects.create_from_params(
                user_id=user.id,
                resume_id=resume_id,
                job_posting_url=job_posting_url
            )

            tailored_resume_serializer = TailoredResumeSerializer(tailored_resume)
            tailored_resume_json_data = {"tailoredResume": tailored_resume_serializer.data}
            
            return Response(
                tailored_resume_json_data,
                status=status.HTTP_201_CREATED
            )
        # TODO remove Exception from error handling here; V1
        except (ParsingError, ValidationError, Exception) as error:
            return Response(
                {
                    "error": error
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
