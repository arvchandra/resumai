from .base import Document


class TxtDocument(Document):
    def get_text(self):
        with open(self.file.path, 'rb') as f:
            return f.read()

    def generate_copy(self):
        pass
