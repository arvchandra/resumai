from abc import ABC, abstractmethod
from resumai.backend.tailor.exceptions import ParsingError


class Document(ABC):
    def __init__(self, file):
        self.file = file

    @abstractmethod
    def get_text(self):
        """
        Parses the file and returns the text content.
        """
        raise ParsingError("Document Type has not been implemented")

    @abstractmethod
    def generate_copy(self):
        pass
