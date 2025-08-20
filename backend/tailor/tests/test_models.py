import pytest


class TestResume:

    @pytest.mark.parametrize("resume_object", [
        "test_arvind_resume.pdf",
        "test_arvind_resume.docx",
        "test_max_resume.pdf",
    ], indirect=True)
    def test_create_resume(self, db, resume_object):
        resume = resume_object
        assert resume.name == "Demo_Resume"
        assert resume.file_type == resume.file.name.split('.')[-1].upper()
        assert resume.get_text() != ""


if __name__ == '__main__':
    pytest.main()
