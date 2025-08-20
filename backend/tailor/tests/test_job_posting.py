import pytest

from tailor.domain.job_posting import LinkedInPosting
from tailor.exceptions import ParsingError


class TestLinkedInPosting:

    class TestFormatUrl:

        @pytest.mark.parametrize("valid_url", [
            "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4272165290",
            "https://www.linkedin.com/jobs/view/4272165290/?alternateChannel=search&"
        ])
        def test_format_valid_urls(self, valid_url):
            formatted_url = "https://www.linkedin.com/jobs/view/4272165290/"
            assert LinkedInPosting(valid_url).url == formatted_url

        @pytest.mark.parametrize("invalid_url", [
            "",
            "www.indeed.com",
            "https://www.linkedin.com/",
            "https://www.linkedin.com/jobs/view/",
            "www.linkedin.com/jobs/view/4272165290/",
        ])
        def test_format_invalid_urls(self, invalid_url):
            with pytest.raises(ParsingError):
                LinkedInPosting(invalid_url)


if __name__ == '__main__':
    pytest.main()
    