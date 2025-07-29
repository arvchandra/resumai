import pymupdf4llm
from resumai.backend.tailor.exceptions import ParsingError

from .base import Document


class PdfDocument(Document):
    def get_text(self):
        resume_text = pymupdf4llm.to_markdown(self.file.path)
        if not resume_text:
            raise ParsingError("Unable to parse resume")

        return resume_text

    def generate_copy(self):
        pass
