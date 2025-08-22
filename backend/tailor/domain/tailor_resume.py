import pymupdf

class TailorPdf:
    def __init__(self, template_resume, bullets_to_redact):
        self.template_resume = template_resume
        self.template_pdf_details = {
            "page_count": 0,
            "width": 0,
            "height": 0
        }
        self.bullets_to_redact = bullets_to_redact

    def tailor_pdf_in_bytes(self):
        try:
            template_pdf_unified = self.generate_unified_pdf()

            self.calculate_spacing(template_pdf_unified)

            redacted_pdf_unified = self.redact_bullets_from_pdf(self.bullets_to_redact, template_pdf_unified)

            tailored_pdf_unified = self.format_tailored_pdf_unified(redacted_pdf_unified)

            tailored_resume = self.split_unified_pdf(tailored_pdf_unified)
            tailored_resume_in_bytes = tailored_resume.tobytes()
            return tailored_resume_in_bytes
        except Exception as e:
            print(f"error: {e}")
            return None

    def generate_unified_pdf(self):
        """
        This function takes a template pdf stored in the FileField of our Resume object and uses it
        to generate a new PDF with only one page that is equal in length to the number of pages in
        the template PDF. This will make it easier to reformat the entire PDF after deleting unnecessary bullet points
        """
        if not self.template_resume or not self.template_resume.file:
            raise FileNotFoundError("Unable to access template resume")

        template_file_path = self.template_resume.file.path
        template_pdf = pymupdf.open(template_file_path)

        page_count = template_pdf.page_count
        page_width = template_pdf[0].rect.width
        page_height = template_pdf[0].rect.height

        if not all((page_count, page_width, page_height)):
            # TODO Error Handling
            raise KeyError("error when attempting to calculate template pdf dimensions")

        self.template_pdf_details = {
            "page_count": page_count,
            "width": page_width,
            "height": page_height
        }

        # creates unified pdf with one page that is as long as there are pages in our template pdf
        template_pdf_unified = self._generate_unified_pdf()
        template_pdf_page_unified = template_pdf_unified[0]

        # Maps pages from template pdf onto unified pdf
        for page in template_pdf:
            # determines how many pages we've already added/need to account for
            page_offset_height = page_height * page.number

            updated_top_of_page = page.rect.y0 + page_offset_height
            updated_bottom_of_page = page.rect.y1 + page_offset_height

            location_on_unified_pdf = pymupdf.Rect(
                page.rect.x0,
                updated_top_of_page,
                page.rect.x1,
                updated_bottom_of_page)

            template_pdf_page_unified.show_pdf_page(location_on_unified_pdf, template_pdf, page.number)

        return template_pdf_unified

    def calculate_spacing(self, template_pdf_unified: pymupdf.Document):
        pass

    def redact_bullets_from_pdf(self, bullets_to_redact: [], template_pdf: pymupdf.Document):
        """
        Identifies where in the page our bullets are that we want to delete, saves the location of where they were
        as a Rect (including the line break spacing between them and the next bullet point), and then redacts them
        """
        pass

    def format_tailored_pdf_unified(self, redacted_pdf: pymupdf.Document):
        """
        This function repositions the remaining text on our redacted pdf onto a new pdf using the location of our
        redacted rects to determine how much we are moving the repositioned text up by.
        """
        pass

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF into the number of pages found on our original template PDF
        """

        return self.template_resume.file

    def _generate_unified_pdf(self):
        page_count, page_width, page_height = self.template_pdf_details.values()
        new_pdf = pymupdf.open()
        new_pdf.new_page(width=page_width, height=page_height * page_count)
        return new_pdf
