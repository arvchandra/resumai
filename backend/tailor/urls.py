from django.urls import path
from tailor.api.views import ParseJobPostingView, UserResumeListView

urlpatterns = [
    path(
        "api/jobposting/",
        ParseJobPostingView.as_view(),
        name="job_posting_text",
    ),
    path(
        "api/users/<int:user_id>/resumes/",
        UserResumeListView.as_view(),
        name="user-resumes",
    )

]
