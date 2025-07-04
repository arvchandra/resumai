from urllib.parse import urlparse

from abc import ABC, abstractmethod


class JobPosting(ABC):
    def __init__(self, url):
        self.url = url
        self.site = urlparse(self.url).netloc
        self.job_id = self.fetch_id()
        
    @abstractmethod
    def fetch_id(self):
        pass

    @abstractmethod
    def get_text(self):
        """
        Scrapes the job posting web page and parses the job description text.
        Returns the job description text.
        """
        pass
