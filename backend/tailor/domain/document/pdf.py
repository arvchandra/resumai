import pymupdf4llm

from .base import Document


class PdfDocument(Document):
    def get_text(self):
        return pymupdf4llm.to_markdown(self.file.path)

    def generate_copy(self):
        pass
