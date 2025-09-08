import pytest


class TestResume:

    @pytest.mark.parametrize("resume_object", [
        "test_arvind_resume.pdf",
        "test_arvind_resume.docx",
        "test_max_resume.pdf",
    ], indirect=True)
    def test_resumes_get_text_passes_for_all_file_types(self, db, resume_object):
        resume = resume_object
        # TODO add expected response doc to compare text; V1
        assert resume.get_text() != ""


if __name__ == '__main__':
    pytest.main()
