import pytest
from pathlib import Path
import shutil

from factories import UserFactory, ResumeFactory


@pytest.fixture(autouse=True)
def media_root_override(settings):
    settings.MEDIA_ROOT = Path(settings.BASE_DIR) / "tailor/tests/test_media_root/uploads"

    yield

    tailored_resumes_path = Path(settings.MEDIA_ROOT) / "tailored_resumes"
    if tailored_resumes_path.exists():
        shutil.rmtree(tailored_resumes_path)


@pytest.fixture
def resume_object(request, db):
    filename = getattr(request, 'param', "test_max_resume.pdf")
    filetype = filename.split('.')[-1].upper()
    filepath = f"resumes/{filename}"
    return ResumeFactory(
        name="Demo_Resume",
        file=filepath,
        file_type=filetype,
        user=UserFactory(username="Test_User"),
    )
