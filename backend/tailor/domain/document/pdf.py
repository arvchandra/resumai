import shutil

import pymupdf4llm
import pymupdf
from shutil import copy
from django.conf import settings
import os

from .base import Document


# HARDCODED_RESUME = "Max_Ingraham_Rakatansky_Work_Resume-11.pdf"
HARDCODED_RESUME = "Arvind_Chandra_-_Resume_-_2025.pdf"
HARDCODED_RESUME_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/uploads/resumes/{HARDCODED_RESUME}"
DESTINATION_DIR_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/tailor/examples/{HARDCODED_RESUME}"
HARDCODED_BULLETS = [
            "●\u200b Completed advanced coursework on Udemy.com to strengthen skills in Django, Python, and React. \n",
            "●\u200b Retained our highest-revenue customer (worth $200,000/year) by resolving critical data integrity issues, which involved writing Django management commands and raw SQL to quickly discover and fix erroneous data mappings. \n",
            "Deputy engineer for async AWS FIFO queue migration in Ruby to address timestamp-sensitive concurrency problem for Service-Level-Agreement(SLA) feature used by enterprise customers; leading post-release handover."
        ]


class PdfDocument(Document):
    def __init__(self, file):
        super().__init__(file)
        self.source_pdf_details = {
            "page_count": None,
            "width": None,
            "height": None
        }
        self.redacted_rects = []
        self.header_breaks = {}

    def get_text(self):
        return pymupdf4llm.to_markdown(self.file.path)

    def generate_copy(self, bullets_to_redact=HARDCODED_BULLETS):
        # Clone PDF of file and save in examples
        # TODO load into a temp memory file
        try:
            os.remove(DESTINATION_DIR_PATH)
            print("file already exists, deleting")
        except OSError:
            print("file not created yet")
            pass

        copied_path = shutil.copy2(HARDCODED_RESUME_PATH, DESTINATION_DIR_PATH)

        # TODO better to create the single page pdf and identify bullets/header spacing when first uploaded
        source_pdf_unified, tailored_pdf_unified = self.generate_unified_pdfs(copied_path)
        source_page_unified, tailored_page_unified = source_pdf_unified[0], tailored_pdf_unified[0]

        redacted_source_page = self.redact_bullets_from_page(bullets_to_redact, source_page_unified)

        try:
            self.format_tailored_pdf_unified(
                redacted_source_page,
                tailored_page_unified,
                source_pdf_unified
            )

            tailored_resume = self.split_unified_pdf(tailored_pdf_unified)
            tailored_resume.save("tailored_resume.pdf")

            source_pdf_unified.save("unified.pdf")
            tailored_pdf_unified.save("unified_tailored.pdf")

            # Can annotate and delete bullet point

            # Page with deleted bullet point corrects page format
        except Exception as e:
            print(f"error: {e}")
            return
        finally:
            source_pdf_unified.close()
            tailored_pdf_unified.close()

    def generate_unified_pdfs(self, path_to_source_pdf):
        """
        This function will take a source PDF use it to generate a new PDF with only one page
        that is equal in length to the number of pages in the source PDF. This will make it easier
        to reformat the entire PDF after deleting unnecessary bullet points
        """
        source_pdf = pymupdf.open(path_to_source_pdf)
        self.source_pdf_details = {
            "page_count": source_pdf.page_count,
            "width": source_pdf[0].rect.width,
            "height": source_pdf[0].rect.height
        }


        # TODO account for header and footer on each page
        # TODO do this on resume upload

        # creates unified pdf with one page that is as long as there are pages in our source pdf
        source_pdf_unified = pymupdf.open()
        source_pdf_page_unified = source_pdf_unified.new_page(
            width=self.source_pdf_details["width"],
            height=self.source_pdf_details["height"] * self.source_pdf_details["page_count"]
        )

        # Adds source pages onto unified pdf
        for page in source_pdf:
            # determines how many pages we've already added/need to account for
            page_offset_height = self.source_pdf_details["height"] * page.number

            location_on_unified_pdf = pymupdf.Rect(
                page.rect.x0,
                page.rect.y0 + page_offset_height,
                page.rect.x1,
                page.rect.y1 + page_offset_height)

            source_pdf_page_unified.show_pdf_page(location_on_unified_pdf, source_pdf, page.number)

        unified_tailored_pdf = pymupdf.open()
        unified_tailored_pdf.new_page(
            width=self.source_pdf_details["width"],
            height=self.source_pdf_details["height"] * self.source_pdf_details["page_count"]
        )

        return source_pdf_unified, unified_tailored_pdf

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF back into the original PDF length
        """

        # unpacks source details dict values and checks if all are defined
        # TODO make sure no values can be 0 or empty
        if not all(list(self.source_pdf_details.values())):
            # TODO Error Handling
            return

        tailored_resume = pymupdf.open()

        for page_number in range(0, self.source_pdf_details["page_count"]):
            page_offset_height = self.source_pdf_details["height"] * page_number
            unified_page_rect = pymupdf.Rect(
                0,
                0 + page_offset_height,
                self.source_pdf_details["width"],
                self.source_pdf_details["height"] + page_offset_height
            )

            resume_page = tailored_resume.new_page(
                -1,
                width=self.source_pdf_details["width"],
                height=self.source_pdf_details["height"]
            )

            resume_page.show_pdf_page(
                resume_page.rect,
                unified_pdf,
                0,
                clip=unified_page_rect
            )

        return tailored_resume

    def redact_bullets_from_page(self, bullets_to_redact: [], source_page: pymupdf.Page):
        # TODO Define default bullet format
        # Note bullets and newline commands not included in blocks, can be left over from deletion,
        # need to read entire line and redact extra characters in order to make sure text block doesn't pick up

        for bullet in bullets_to_redact:
            bullet_rect = None
            # TODO helper method for bullet characters and \n lines
            for rect in source_page.search_for(bullet):
                bullet_rect = self._combine_rects(bullet_rect, rect)

            if bullet_rect:
                source_page.add_redact_annot(bullet_rect)
                self.redacted_rects.append(bullet_rect)
            else:
                continue

        print(f"list of redacted Rects = {self.redacted_rects}")
        result = source_page.apply_redactions()
        if not result:
            # TODO error handling
            print("could not find any bullets on the page")

        return source_page

    def format_tailored_pdf_unified(self, redacted_page: pymupdf.Page, tailored_page_unified: pymupdf.Page, source_pdf_unified: pymupdf.Document):
        redacted_index = 0
        offset_by = 0

        for text_block in redacted_page.get_text("blocks"):
            print(text_block)
            source_rect = self._get_rect(text_block)

            # handle when nothing to redact or we've redacted everything
            if self.redacted_rects and redacted_index < len(self.redacted_rects):
                redacted_rect = self.redacted_rects[redacted_index]
                if source_rect.y0 > redacted_rect.y1:
                    print("we found a moment where our block is lower")
                    print(text_block)

                    # calculate how much we need to offset by
                    redacted_offset = redacted_rect.height
                    line_break_offset = source_rect.y0 - redacted_rect.y1
                    # TODO handle two column offset
                    offset_by += redacted_offset + line_break_offset
                    redacted_index += 1
                    # print(current_redaction)
                    # print(current_redaction.height)
                    # print(f"new offset is {offset_by}")

            # TODO handle header footer offset
            updated_rect = self._get_rect(text_block, offset_by)
            # print(f"source rect is {source_rect}")
            # print(f"updated rect is {updated_rect}")
            tailored_page_unified.show_pdf_page(
                updated_rect,
                source_pdf_unified,
                redacted_page.number,
                clip=source_rect
            )

    @staticmethod
    def _combine_rects(existing_rect: pymupdf.Rect, new_rect: pymupdf.Rect):
        if not existing_rect:
            return new_rect

        new_x0 = min(existing_rect.x0, new_rect.x0)
        new_y0 = min(existing_rect.y0, new_rect.y0)
        new_x1 = max(existing_rect.x1, new_rect.x1)
        new_y1 = max(existing_rect.y1, new_rect.y1)

        return pymupdf.Rect(new_x0, new_y0, new_x1, new_y1)

    @staticmethod
    def _get_rect(block, offset=0):
        return pymupdf.Rect(block[0], block[1] - offset, block[2], block[3] - offset)



