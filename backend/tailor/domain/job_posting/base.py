from urllib.parse import urlparse

from abc import ABC, abstractmethod
from tailor.exceptions import ParsingError


class JobPosting(ABC):
    def __init__(self, url):
        self.url = self.format_url(url)
        self.site = urlparse(self.url).netloc

    @abstractmethod
    def format_url(self, url):
        return url

    @abstractmethod
    def get_text(self):
        """
        Scrapes the job posting web page and parses the job description text.
        Returns the job description text.
        """
        raise ParsingError("Job Posting Site has not been implemented yet")
