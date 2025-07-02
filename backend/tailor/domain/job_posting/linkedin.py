from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
from .base import JobPosting

JOB_POSTING_PATH = "https://www.linkedin.com/jobs/view"
JOB_ID_QUERY_PARAM = "currentJobId"


def fetch_job_id(self):
    site = self.site
    return self.SITES[site]() if site in self.SITES else None


class LinkedInPosting(JobPosting):
    def __init__(self, url):
        self.url = url
        self.site = urlparse(self.url).netloc
        self.job_id = self.fetch_id()

    def fetch_id(self):
        try:
            url = urlparse(self.url)
            query_params = parse_qs(url.query)
            path_array = url.path.split('/')
            job_id_query_bytes = bytes(JOB_ID_QUERY_PARAM)

            # When URL is of the format https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4259433658
            if query_params.get(job_id_query_bytes):
                return query_params[job_id_query_bytes]
            else:
                # When URL is of the format https://www.linkedin.com/jobs/view/4259447405/?alternateChannel=search
                return path_array[-1] if path_array[-2] == "view" else None
        except KeyError as e:
            # TODO log error
            pass

    def parse_job_posting(self):
        # Will attempt to try without headless browsers since it's possible the problem only
        # emerges when we try expired applications. Will test with this for now
        job_posting_url = f"{JOB_POSTING_PATH}/{self.job_id}"
        response = requests.get(job_posting_url)

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        job_posting_html = soup.find('div', class_='description__text')
        job_posting_text = job_posting_html.get_text(strip=True, separator='\n') if job_posting_html else ""

        return job_posting_text
