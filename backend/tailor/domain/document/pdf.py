import shutil

import pymupdf4llm
import pymupdf
import os
from django.conf import settings

from .base import Document


# HARDCODED_RESUME = "Max_Ingraham_Rakatansky_Work_Resume-11.pdf"
HARDCODED_RESUME = "Arvind_Chandra_-_Resume_-_2025.pdf"
HARDCODED_RESUME_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/uploads/resumes/{HARDCODED_RESUME}"
DESTINATION_DIR_PATH = f"/Users/maxingraham-rakatansky/resumai_django/resumai/backend/tailor/examples/{HARDCODED_RESUME}"
HARDCODED_BULLETS = [
            "●\u200b Completed advanced coursework on Udemy.com to strengthen skills in Django, Python, and React. \n",
            "●\u200b Retained our highest-revenue customer (worth $200,000/year) by resolving critical data integrity issues, which involved writing Django management commands and raw SQL to quickly discover and fix erroneous data mappings. \n",
            "●\u200b Upgraded our Nextgov and Government Executive websites to a modern responsive web design, which were both subsequently nominated for a web design award on Folio. \n"
            "●\u200b Interviewed and hired senior Django developers. \n"
            "Deputy engineer for async AWS FIFO queue migration in Ruby to address timestamp-sensitive concurrency problem for Service-Level-Agreement(SLA) feature used by enterprise customers; leading post-release handover."
        ]


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
        return pymupdf4llm.to_markdown(self.file.path)

    def generate_copy(self, bullets_to_redact=HARDCODED_BULLETS):
        # Clone PDF of file and save in examples
        # TODO replace with Resume fetch
        try:
            os.remove(DESTINATION_DIR_PATH)
            print("file already exists, deleting")
        except OSError:
            print("file not created yet")
            pass

        copied_path = shutil.copy2(HARDCODED_RESUME_PATH, DESTINATION_DIR_PATH)

        # TODO better to create the single page pdf and identify bullets/header spacing when first uploaded
        try:
            source_pdf_unified = self.generate_unified_pdf(copied_path)
            redacted_pdf_unified = self.redact_bullets_from_pdf(bullets_to_redact, source_pdf_unified)
            tailored_pdf_unified = self.format_tailored_pdf_unified(redacted_pdf_unified)

            tailored_resume = self.split_unified_pdf(tailored_pdf_unified)

            # TODO remove after testing
            source_pdf_unified.save("unified.pdf")
            tailored_pdf_unified.save("unified_tailored.pdf")

            tailored_resume.save("tailored_resume.pdf")
        except Exception as e:
            print(f"error: {e}")
            return
        finally:
            source_pdf_unified.close()
            tailored_pdf_unified.close()
            tailored_resume.close()

    def generate_unified_pdf(self, path_to_source_pdf):
        """
        This function takes a source PDF and uses it to generate a new PDF with only one page
        that is equal in length to the number of pages in the source PDF. This will make it easier
        to reformat the entire PDF after deleting unnecessary bullet points
        """

        source_pdf = pymupdf.open(path_to_source_pdf)
        self.source_pdf_details = {
            "page_count": source_pdf.page_count,
            "width": source_pdf[0].rect.width,
            "height": source_pdf[0].rect.height
        }

        if not all(list(self.source_pdf_details.values())):
            # TODO Error Handling
            raise KeyError

        # creates unified pdf with one page that is as long as there are pages in our source pdf
        source_pdf_unified = pymupdf.open()
        source_pdf_page_unified = source_pdf_unified.new_page(
            width=self.source_pdf_details["width"],
            height=self.source_pdf_details["height"] * self.source_pdf_details["page_count"]
        )

        header_from_this_page = None
        footer_from_previous_page = None

        # Maps source pages onto unified pdf
        for page in source_pdf:
            # determines how many pages we've already added/need to account for
            page_offset_height = self.source_pdf_details["height"] * page.number

            updated_top_of_page = page.rect.y0 + page_offset_height
            updated_bottom_of_page = page.rect.y1 + page_offset_height

            location_on_unified_pdf = pymupdf.Rect(
                page.rect.x0,
                updated_top_of_page,
                page.rect.x1,
                updated_bottom_of_page)

            source_pdf_page_unified.show_pdf_page(location_on_unified_pdf, source_pdf, page.number)

            # calculates page break spacing on unified pdf (if applicable)
            header_height, footer_height = self.calculate_page_break_spacing(page)
            header_from_this_page = updated_top_of_page + header_height

            # checks if we already have a footer from the previous page and can calculate the combined volume
            if footer_from_previous_page and footer_from_previous_page < header_from_this_page:
                rect = pymupdf.Rect(0, footer_from_previous_page, self.source_pdf_details["width"], header_from_this_page)
                self.page_break_rects.append(rect)

            footer_from_previous_page = updated_bottom_of_page - footer_height

        return source_pdf_unified

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF back into the original PDF length
        """
        # unpacks source details dict values and checks if all are defined
        if not all(list(self.source_pdf_details.values())):
            # TODO Error Handling
            raise Exception

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
                clip=unified_page_rect
            )

        return tailored_resume

    def redact_bullets_from_pdf(self, bullets_to_redact: [], source_pdf: pymupdf.Document):
        # TODO Define default bullet format
        # Note bullets and newline commands not included in blocks, can be left over from deletion,
        # need to read entire line and redact extra characters in order to make sure text block doesn't pick up
        source_page = source_pdf[0]

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

        return source_pdf

    def format_tailored_pdf_unified(self, redacted_pdf: pymupdf.Document):
        redacted_page = redacted_pdf[0]

        tailored_pdf_unified = pymupdf.open()
        tailored_pdf_unified.new_page(
            width=self.source_pdf_details["width"],
            height=self.source_pdf_details["height"] * self.source_pdf_details["page_count"]
        )

        tailored_page_unified = tailored_pdf_unified[0]

        redacted_index = 0
        offset_by = 0

        for text_block in redacted_page.get_text("blocks"):
            # print(text_block)
            source_rect = self._get_rect(text_block)

            # handle when nothing to redact or we've redacted everything
            if self.redacted_rects and redacted_index < len(self.redacted_rects):
                redacted_rect = self.redacted_rects[redacted_index]
                if source_rect.y0 > redacted_rect.y1:
                    # print("we found a moment where our block is lower")
                    # print(text_block)

                    # calculate how much we need to offset by
                    redacted_offset = redacted_rect.height
                    line_break_offset = source_rect.y0 - redacted_rect.y1
                    # TODO handle two column offset
                    offset_by += redacted_offset + line_break_offset
                    redacted_index += 1
                    # print(current_redaction)
                    # print(current_redaction.height)
                    # print(f"new offset is {offset_by}")

            updated_rect = self.calculate_updated_rect(text_block, offset_by)

            # print(f"source rect is {source_rect}")
            # print(f"updated rect is {updated_rect}")
            tailored_page_unified.show_pdf_page(
                updated_rect,
                redacted_pdf,
                clip=source_rect
            )

        return tailored_pdf_unified

    def calculate_updated_rect(self, text_block, offset_by):
        updated_rect = self._get_rect(text_block, offset_by)

        # check if updated rectangle intersects with a page break
        for page_break_rect in self.page_break_rects:
            if page_break_rect.intersects(updated_rect):
                # TODO break up only part of text block that overlaps
                updated_offset = offset_by + page_break_rect.height
                updated_rect = self._get_rect(text_block, updated_offset)

        return updated_rect

    @staticmethod
    def calculate_page_break_spacing(page: pymupdf.Page):
        """
        returns the distance (in pixels) of the text closest to the top of the page (bottom of header)
        and the bottom of the page (top of footer)
        """

        # Note: get_text("blocks") returns array of tuples in the form:
        # (x0, y0, x1, y1, "lines in the block", block_no, block_type)

        # distance from top of the page to the text block with the lowest y0 value (bottom of header)
        top_of_page = 0
        bottom_of_header = min(text_block[1] for text_block in page.get_text("blocks"))
        header_height = top_of_page + bottom_of_header

        # distance from the bottom of the page to the text block with the largest y1 value (top of footer)
        bottom_of_page = page.rect.height
        top_of_footer = max(text_block[3] for text_block in page.get_text("blocks"))
        footer_height = bottom_of_page - top_of_footer

        return header_height, footer_height

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



