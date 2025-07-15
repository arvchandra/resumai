from django.urls import path
from tailor.api.views import (
    UserResumeUploadView, 
    TailorResumeView,
    UserResumeListView
)

urlpatterns = [
    path(
        "users/<int:user_id>/resumes/",
        UserResumeListView.as_view(),
        name="user-resumes",
    ),
    path(
        "users/<int:user_id>/resumes/upload",
        UserResumeUploadView.as_view(),
        name="user-resume-upload",
    ),
    path(
        "users/<int:user_id>/tailor-resume",
        TailorResumeView.as_view(),
        name="tailor-resume",
    ),
]
