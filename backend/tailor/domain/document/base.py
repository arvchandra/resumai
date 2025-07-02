from abc import ABC, abstractmethod


class Document(ABC):
    @abstractmethod
    def parse_file_text(self, file):
        pass

    @abstractmethod
    def generate_copy(self):
        pass
