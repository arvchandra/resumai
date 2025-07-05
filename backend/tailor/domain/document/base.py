from abc import ABC, abstractmethod


class Document(ABC):
    def __init__(self, file):
        self.file = file

    @abstractmethod
    def get_text(self):
        """
        Parses the file and returns the text content.
        """
        pass

    @abstractmethod
    def generate_copy(self):
        pass
