import shutil
from pathlib import Path
import pytest
from django.conf import settings
from django.contrib.auth.models import User
from tailor.models import Resume, TailoredResume


@pytest.fixture(autouse=True)
def media_root_override(settings):
    settings.MEDIA_ROOT = Path(settings.BASE_DIR) / "tailor/tests/test_media_root/uploads"

    yield

    tailored_resumes_path = Path(settings.MEDIA_ROOT) / "tailored_resumes"
    if tailored_resumes_path.exists():
        shutil.rmtree(tailored_resumes_path)


@pytest.fixture
def user_data(db) -> User:
    return User.objects.create_user("Test_User")


@pytest.fixture
def resume_data( request, db, user_data):
    filename = request.param
    filetype = filename.split('.')[-1].upper()
    filepath = f"resumes/{filename}"
    return {
        "name": "Demo_Resume",
        "file": filepath,
        "file_type": filetype,
        "user": user_data,
    }


class TestResume:

    @pytest.mark.parametrize("resume_data", [
        "test_arvind_resume.pdf",
        "test_arvind_resume.docx",
        "test_max_resume.pdf",
    ], indirect=True)
    def test_create_resume(self, db, resume_data):
        resume = Resume(**resume_data)
        assert resume.name == "Demo_Resume"
        assert resume.file_type == resume.file.name.split('.')[-1].upper()
        assert resume.get_text() != ""


if __name__ == '__main__':
    pytest.main()