from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
from .base import JobPosting

JOB_POSTING_PATH = "https://www.linkedin.com/jobs/view"
JOB_ID_QUERY_PARAM = "currentJobId"


class LinkedInPosting(JobPosting):
    def fetch_id(self):
        try:
            url = urlparse(self.url)
            query_params = parse_qs(url.query)
            path_array = url.path.split('/')

            # When URL is of the format https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4259433658
            if query_params.get(JOB_ID_QUERY_PARAM):
                return query_params[JOB_ID_QUERY_PARAM][0]
            else:
                # When URL is of the format https://www.linkedin.com/jobs/view/4259447405/?alternateChannel=search
                return path_array[-2] if path_array[-3] == "view" else None
        except KeyError as e:
            # TODO log error
            pass

    def get_text(self):
        # Will attempt to try without headless browsers since it's possible the problem only
        # emerges when we try expired applications. Will test with this for now

        #TODO move this into format_url method and refactor to raise ParsingError
        if not self.job_id:
            print("unable to parse Job ID")
            return

        job_posting_url = f"{JOB_POSTING_PATH}/{self.job_id}"
        response = requests.get(job_posting_url)

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        job_posting_html = soup.find('div', class_='description__text')
        job_posting_text = job_posting_html.get_text(strip=True, separator='\n') if job_posting_html else ""

        return job_posting_text
