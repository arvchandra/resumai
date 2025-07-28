import os

from openai import OpenAI
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import FileResponse
from django.contrib.auth.models import User
from django.conf import settings

from tailor.api.serializers import FileUploadSerializer, ResumeSerializer, TailoredResumeSerializer
from tailor.domain.document import DocumentFactory
from tailor.domain.job_posting import LinkedInPosting
from tailor.models import Resume, TailoredResume


class ParsingError(Exception):
    pass


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
        POST /tailor/users/<int:user_id>/resume/upload/
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

            # Get the file type (uppercase file extension)
            _, extension = os.path.splitext(uploaded_file.name)
            file_type = str(extension[1:]).upper()  # excludes the dot (e.g., 'DOCX')

            # Save the file via the Resume model
            new_resume_upload = Resume()
            new_resume_upload.name = uploaded_file.name
            new_resume_upload.file = uploaded_file
            new_resume_upload.file_type = file_type
            new_resume_upload.user = User.objects.get(id=user_id)  # TODO: Get user from auth
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
        user_id = self.kwargs["user_id"]
        return TailoredResume.objects.filter(user__id=user_id).order_by('-created_at')


class TailoredResumeDownloadView(APIView):
    def get(self, request, *args, **kwargs):
        tailored_resume_id, user_id = self.kwargs["tailored_resume_id"], self.kwargs["user_id"]

        try:
            tailored_resume = TailoredResume.objects.get(pk=tailored_resume_id, user_id=user_id)

            return FileResponse(tailored_resume.file.open(), 'rb', as_attachment=True)
        except TailoredResume.DoesNotExist:
            # TODO error handling
            return Response(
                {
                    "error": "File is not accessible"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except TailoredResume.MultipleObjectsReturned:
            # TODO error handling
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
    - Builds a prompt containing the parsed resume text and job description, and sends
      the request to the AI API.
    - Receives the response from the AI API and formats the tailored resume content.
    - Responds with the formatted tailored resume content if the process was successful.

    Example request:
        POST /tailor/users/<int:user_id>/tailor-resume
        Content-Type: application/json
        Body:
            {
                "resume_id": 123,
                "job_posting_url": "https://www.linkedin.com/jobs/view/4117993213"
            }

    Responses:
        200 OK
        400 Bad Request
    """

    def post(self, request, *args, **kwargs):
        user_id: int = int(self.kwargs["user_id"])
        resume_id: int = int(request.data["resume_id"])
        job_posting_url: str = request.data["job_posting_url"]

        # Validate that logged in user matches the user referenced in the request URL
        # TODO: request.user.id == user_id  (must implement user login/auth first)

        # Validate that the resume exists and it is for the current user
        resume = None
        try:
            resume = Resume.objects.get(id=resume_id, user_id=user_id)
        except Resume.DoesNotExist:
            raise NotFound("Resume not found.")

        # TODO: Move this logic into JobPosting class
        # Validate that the job posting URL is a LinkedIn URL
        if "linkedin.com" not in job_posting_url:
            raise ValidationError("Invalid job posting URL. Must be from www.linkedin.com")

        try:
            # Get text content of resume
            resume_document = DocumentFactory.create(resume.file)
            resume_text = resume_document.get_text()
            # TODO extract ParsingError
            if not resume_text:
                raise ParsingError("Unable to parse resume")

            # Call job posting scraper + parser
            linkedin_job_posting = LinkedInPosting(job_posting_url)
            job_posting_text = linkedin_job_posting.get_text()

            # Send request to AI API and receive tailored resume response -- Max
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = {
                    "id": "pmpt_686808032cc88193914ee3c0726c26fc06b6bcce04c3ec55",
                    "version": "5",
                    "variables": {
                        "job_posting": job_posting_text,
                        "resume": resume_text
                    }
                }
            # response = client.responses.create(prompt=prompt)
            response = {
                "output":
            }
            if not all(response["company"], response["role"]):


            tailored_resume = resume_document.generate_copy()

            return Response(
                {
                    "user_id": user_id,
                    "resume_name": resume.name,
                    "job_posting_url": job_posting_url,
                    "resume_text": resume_text,
                    "job_posting_text": job_posting_text,
                    # "output_text": response.output_text,
                },
                status=status.HTTP_200_OK
            )
        except ParsingError as error:
            # TODO add error handling
            return Response(
                {
                    "error": error
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as error:
            # TODO add error handling
            return Response(
                {
                    "error": error
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
