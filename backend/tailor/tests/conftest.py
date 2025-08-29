import pytest
from pathlib import Path
import shutil

from factories import UserFactory, ResumeFactory

DEFAULT_RESUME_FILENAME = "test_max_resume.pdf"


@pytest.fixture(autouse=True)
def media_root_override(settings):
    settings.MEDIA_ROOT = Path(settings.BASE_DIR) / "tailor/tests/test_media_root/uploads"

    yield

    tailored_resumes_path = Path(settings.MEDIA_ROOT) / "tailored_resumes"
    if tailored_resumes_path.exists():
        shutil.rmtree(tailored_resumes_path)


TEST_RESUMES = [
    "test_arvind_resume.pdf",
    "test_max_resume.pdf"
]


@pytest.fixture(params=TEST_RESUMES)
def resume_object(request, db):
    filename = getattr(request, 'param', DEFAULT_RESUME_FILENAME)
    filetype = filename.split('.')[-1].upper()
    filepath = f"resumes/{filename}"
    return ResumeFactory(
        name="Demo_Resume",
        file=filepath,
        file_type=filetype,
        user=UserFactory(username="Test_User"),
    )
