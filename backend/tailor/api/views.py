from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


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
