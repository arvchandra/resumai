import os

from tailor.domain.document.constants import DOCX, PDF, TEX, TXT
from tailor.domain.document import (
    Document,
    DocxDocument,
    PdfDocument,
    TexDocument,
    TxtDocument
)

# Map of file types to Document subclasses
FILE_TYPE_DOCUMENT_SUBCLASS = {
    DOCX: DocxDocument,
    PDF: PdfDocument,
    TEX: TexDocument,
    TXT: TxtDocument
}


class DocumentFactory:
    @staticmethod
    def create(file) -> Document:
        """
        Returns an instance of the appropriate Document subclass
        initialized with the provided file.
        """
        # Get the file type (uppercase file extension)
        _, extension = os.path.splitext(file.name)
        file_type = str(extension[1:]).upper()  # excludes the dot (e.g., 'DOCX')

        document_class = FILE_TYPE_DOCUMENT_SUBCLASS[file_type]
        return document_class(file)
