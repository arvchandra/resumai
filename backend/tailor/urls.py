from django.urls import path
from tailor.api.views import ParseJobPostingView

urlpatterns = [
    path(
        "api/jobposting/",
        ParseJobPostingView.as_view(),
        name="job_posting_text",
    ),
]
