from .base import Document
import docx


class DocxDocument(Document):
    def parse_file_text(self):
        doc = docx.Document(self.file_path)
        for paragraph in doc.paragraphs:
            print(paragraph.text)

    def generate_copy(self):
        pass
