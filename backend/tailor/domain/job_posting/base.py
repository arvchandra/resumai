from abc import ABC, abstractmethod


class JobPosting(ABC):
    @abstractmethod
    def fetch_id(self):
        pass

    @abstractmethod
    def parse_job_posting(self):
        pass
