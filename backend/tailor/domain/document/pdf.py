from .base import Document
import pymupdf4llm


class PdfDocument(Document):
    def parse_file_text(self, file):
        print(pymupdf4llm.to_markdown(file))

    def generate_copy(self):
        pass
