import shutil

import pymupdf4llm
from tailor.exceptions import ParsingError


from .base import Document


class PdfDocument(Document):
    def __init__(self, file):
        super().__init__(file)
        self.source_pdf_details = {
            "page_count": 0,
            "width": 0,
            "height": 0
        }
        self.redacted_rects = []
        self.page_break_rects = []

    def get_text(self):
        resume_text = pymupdf4llm.to_markdown(self.file.path)
        if not resume_text:
            raise ParsingError("Unable to parse resume")

        return resume_text

    def generate_copy(self, bullets_to_redact):
        # Clone PDF of file and save in examples
        pass



