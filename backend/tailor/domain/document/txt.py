from .base import Document


class TxtDocument(Document):
    def parse_file_text(self, file):
        with open(file, 'rb') as f:
            print(f.read())

    def generate_copy(self):
        pass
