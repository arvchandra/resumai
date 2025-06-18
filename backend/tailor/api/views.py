from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tailor.api.serializers import ResumeSerializer
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