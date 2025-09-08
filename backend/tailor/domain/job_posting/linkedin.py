from urllib.parse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup
import requests
import re
from tailor.exceptions import ParsingError

from .base import JobPosting

JOB_POSTING_PATH = "https://www.linkedin.com/jobs/view"
JOB_POSTING_REGEX = '^https://www.linkedin.com/jobs/view/[0-9]{10}'
JOB_ID_QUERY_PARAM = "currentJobId"


class LinkedInPosting(JobPosting):
    def format_url(self, url):
        try:
            parsed_url = urlparse(url)

            # When URL is of the format https://www.linkedin.com/jobs/view/4259447405/?alternateChannel=search
            if re.search(JOB_POSTING_REGEX, url):
                reformatted_url = urljoin(url, parsed_url.path)
                return reformatted_url

            # When URL is of the format https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4259433658
            query_params = parse_qs(parsed_url.query)
            job_ids = query_params.get(JOB_ID_QUERY_PARAM)
            if job_ids:
                reformatted_url = f"{JOB_POSTING_PATH}/{job_ids[0]}/"
                return reformatted_url

            # When the URL is anything else
            raise ParsingError("Unable to parse job posting")
        except (AttributeError, TypeError) as e:
            # TODO log error; V1 logging
            raise e

    def get_text(self):
        # Will attempt to try without headless browsers since it's possible the problem only
        # emerges when we try expired applications. Will test with this for now
        response = requests.get(self.url)

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        job_posting_html = soup.find('div', class_='description__text')
        job_posting_text = job_posting_html.get_text(strip=True, separator='\n') if job_posting_html else ""

        # handles when we have an expired Job posting
        if not job_posting_text:
            raise ParsingError("Unable to identify job text, job posting possibly expired")

        return job_posting_text
