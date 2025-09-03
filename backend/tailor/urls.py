from django.urls import path
from tailor.api.views import (
    UserResumeUploadView, 
    TailorResumeView,
    TailoredResumeListView,
    TailoredResumeDownloadView,
    UserResumeListView
)

urlpatterns = [
    path(
        "resumes/",
        UserResumeListView.as_view(),
        name="user-resumes",
    ),
    path(
        "resumes/upload/",
        UserResumeUploadView.as_view(),
        name="user-resume-upload",
    ),
    path(
        "tailor-resume/",
        TailorResumeView.as_view(),
        name="tailor-resume",
    ),
    path(
        "tailored-resumes/",
        TailoredResumeListView.as_view(),
        name="tailored-resumes",
    ),
    path(
        "tailored-resume/<int:tailored_resume_id>/download/",
        TailoredResumeDownloadView.as_view(),
        name="tailored-resume-download",
    ),
]
