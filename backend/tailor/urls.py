from django.urls import path
from tailor.api.views import (
    UserResumeUploadView, 
    ParseJobPostingView, 
    TailorResumeView,
    UserResumeListView
)

urlpatterns = [
    path(
        "jobposting/",
        ParseJobPostingView.as_view(),
        name="job_posting_text",
    ),
    path(
        "users/<int:user_id>/resume/",
        UserResumeListView.as_view(),
        name="user-resumes",
    ),
    path(
        "users/<int:user_id>/resume/upload",
        UserResumeUploadView.as_view(),
        name="user-resume-upload",
    ),
    path(
        "users/<int:user_id>/tailor-resume",
        TailorResumeView.as_view(),
        name="tailor-resume",
    ),
]
