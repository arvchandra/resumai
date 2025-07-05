from .base import Document
from .docx import DocxDocument
from .pdf import PdfDocument
from .tex import TexDocument
from .txt import TxtDocument
from .factory import DocumentFactory

__all__ = ["Document", "DocxDocument", "PdfDocument", "TexDocument", "TxtDocument", "DocumentFactory"]
