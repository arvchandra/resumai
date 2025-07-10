import shutil

import pymupdf4llm
import pymupdf
from shutil import copy
from django.conf import settings
import os

from .base import Document


HARDCODED_RESUME = "Max_Ingraham_Rakatansky_Work_Resume-11.pdf"
HARDCODED_RESUME_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/uploads/resumes/{HARDCODED_RESUME}"
DESTINATION_DIR_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/tailor/examples/{HARDCODED_RESUME}"


class PdfDocument(Document):
    def get_text(self):
        return pymupdf4llm.to_markdown(self.file.path)

    def generate_copy(self):
        # Clone PDF of file and save in examples

        # TODO load into a temp memory file
        try:
            os.remove(DESTINATION_DIR_PATH)
            print("file already exists, deleting")
        except OSError:
            print("file not created yet")
            pass

        copied_pdf = shutil.copy2(HARDCODED_RESUME_PATH, DESTINATION_DIR_PATH)

        doc = pymupdf.open(copied_pdf)
        page = doc[0]
        bullet = "• Deputy engineer for async AWS FIFO queue migration in Ruby to address timestamp-sensitive concurrency problem for Service-Level-Agreement(SLA) feature used by enterprise customers; leading post-release handover."
        for rect in page.search_for(bullet):
            print(rect)
            page.add_redact_annot(rect)

        print("attempting to redact annotations")
        result = page.apply_redactions()
        for block in page.get_text("blocks"):
            print(block)

        print(result)
        doc.save("edited.pdf")
        doc.close()
        # if above fails
        # with default_storage.open(obj.file.name) as f:
        #     data = f.read()
        #
        # doc = pymupdf.Document(stream=data)


        # Can annotate and delete bullet point

        # Page with deleted bullet point corrects page format

        # Can combine pdf into one page

        # Can split PDF into multiple pages based on normal page size



