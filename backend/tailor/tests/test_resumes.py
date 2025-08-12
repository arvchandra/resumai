import pytest

from tailor.models import Resume


# @pytest.mark.django_db
# def test_resume:
#

def test_the_obvious():
    assert True == True


class TestUserResumeUploadView:
    def test_resume_list_view(self):
        assert True == True

    def test_returns_empty_when_no_resumes(self):
        assert True == True


if __name__ == '__main__':
    pytest.main()