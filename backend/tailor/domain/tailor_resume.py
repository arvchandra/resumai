import pymupdf
from scipy.stats import mode

def tailor_resume(response, file_type ='pdf'):
    pass


class TailorPdf:
    def __init__(self, template_resume, bullets_to_redact):
        self.template_resume = template_resume
        self.template_pdf_details = {
            "page_count": 0,
            "width": 0,
            "height": 0
        }
        self.bullet_line_break = 0
        self.redacted_rects = []
        self.page_break_rects = []
        self.tailored_resume_in_bytes = self.tailor_pdf_in_bytes(bullets_to_redact)

    def tailor_pdf_in_bytes(self, bullets_to_redact):
        try:
            template_pdf_unified = self.generate_unified_pdf()

            self.calculate_spacing(template_pdf_unified)

            redacted_pdf_unified = self.redact_bullets_from_pdf(bullets_to_redact, template_pdf_unified)

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
        if not (self.template_resume or self.template_resume.file):
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
        template_pdf_unified = self._generate_unified_pdf(*self.template_pdf_details.values())
        template_pdf_page_unified = template_pdf_unified[0]

        # Maps template pages onto unified pdf
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
        # TODO column spacing https://github.com/pymupdf/PyMuPDF/discussions/2259#discussioncomment-6669190

        self.page_break_rects = self.calculate_page_break_spacing(template_pdf_unified[0])

    def calculate_page_break_spacing(self, template_page_unified: pymupdf.Page):
        """
        returns a list of page_break_rects that span from the bottom of text on a previous page (top of footer)
        to the top of text on the current page (bottom of header)
        """

        # Note: get_text("blocks") returns array of tuples in the form:
        # (x0, y0, x1, y1, "lines in the block", block_no, block_type)

        page_count, page_width, page_height = self.template_pdf_details.values()
        page_break_heights = [page_height * i for i in range(1, page_count + 1)]
        page_break_index = 0
        page_break_rects = []

        previous_text_rect = None
        for text_block in template_page_unified.get_text("blocks"):
            current_text_rect = self._get_rect(text_block)

            # If we don't have a previous text block or we've reached the end of our page_break_rects list
            if not previous_text_rect or page_break_index == len(page_break_heights):
                previous_text_rect = current_text_rect
                continue

            # when we encounter a text block that is below a page break
            if current_text_rect.y0 > page_break_heights[page_break_index]:
                # We want to calculate the distance between the last text block on the previous page
                # and the first text block on the current page and create a Rect that matches it
                page_break_x0 = 0
                page_break_y0 = previous_text_rect.y1
                page_break_x1 = page_width
                page_break_y1 = current_text_rect.y0
                page_break_rects.append(
                    self._get_rect([page_break_x0, page_break_y0, page_break_x1, page_break_y1])
                )

                page_break_index += 1

            previous_text_rect = current_text_rect

        return page_break_rects

    def redact_bullets_from_pdf(self, bullets_to_redact: [], template_pdf: pymupdf.Document):
        template_page = template_pdf[0]

        for bullet in bullets_to_redact:
            redacted_rect = self._combine_rects(template_page.search_for(bullet))

            if not redacted_rect:
                continue

            redacted_rect = self.maybe_add_line_break(redacted_rect, template_page)

            self.redacted_rects.append(redacted_rect)
            template_page.add_redact_annot(redacted_rect)

        self.redacted_rects = sorted(self.redacted_rects, key=lambda rect: rect.y0)

        result = template_page.apply_redactions()
        if not result:
            # TODO error handling
            print("could not find any bullets on the page")

        template_pdf.reload_page(template_page)
        return template_pdf

    def maybe_add_line_break(self, redacted_rect: pymupdf.Rect, template_page: pymupdf.Page):
        """
        This function checks if we can find any text below our redacted rect. If so, we will calculate
        the empty space between them before extending the redacted rect to cover this whitespace. This
        will allow us to account for it later when we are repositioning the text below it.

        If we do not find any text below our redacted rect, we return the redacted rect as is
        """

        # use a negative offset to generate a rect of the same size underneath our redacted rect
        offset_by_redacted_rect = (redacted_rect.height + 1) * -1
        redacted_block = list(redacted_rect)
        rect_underneath_redacted_rect = self._get_rect(redacted_block, offset_by_redacted_rect)

        # search new rect for any text, rebuilding text rect to only encapsulate that text if found
        text_underneath_redacted_rect = template_page.get_textbox(rect_underneath_redacted_rect)
        text_rect = self._combine_rects(template_page.search_for(text_underneath_redacted_rect))

        if text_rect and not text_rect.intersects(redacted_rect):
            # extend our redacted rect to just above our text_rect
            redacted_rect = self._get_rect([
                redacted_rect.x0,
                redacted_rect.y0,
                redacted_rect.x1,
                text_rect.y0 - 0.000001
            ])

        return redacted_rect

    def format_tailored_pdf_unified(self, redacted_pdf: pymupdf.Document):
        """
        This function repositions the remaining text on our redacted pdf onto a new pdf using the location of our
        redacted rects to increase add how much we are moving the repositioned text up by

        Example:
        Template PDF
        - A
        - B
        - C
        - D

        Redacted PDF
        - A
             <- B has been redacted
             <- C has been redacted
        - D  <- needs to be repositioned on the new pdf by the height of B + C

        Tailored PDF
        - A
        - D
        """
        redacted_page = redacted_pdf[0]

        tailored_pdf_unified = self._generate_unified_pdf(*self.template_pdf_details.values())
        tailored_page_unified = tailored_pdf_unified[0]

        redacted_rect_index = 0
        total_offset_by = 0
        for text_block in redacted_page.get_text("blocks"):
            text_rect = self._get_rect(text_block)

            redacted_offset, redacted_rect_index = self.calculate_text_rect_offset(redacted_rect_index, text_rect)
            total_offset_by += redacted_offset

            # TODO account for self.page_break_rects
            repositioned_text_rect = self._get_rect(text_block, total_offset_by)
            interim_pdf_unified = self.isolate_repositioned_rect(repositioned_text_rect, redacted_pdf, text_rect)

            tailored_page_unified.show_pdf_page(
                repositioned_text_rect,
                interim_pdf_unified,
                clip=repositioned_text_rect
            )

            interim_pdf_unified.close()

        return tailored_pdf_unified

    def calculate_text_rect_offset(self, redacted_rect_index: int, text_block_rect: pymupdf.Rect):
        """
        This function is meant to use our self.page_break_rects to reposition the rect passed in
        if it falls into one of the rects that capture our footer + header spacing. If it does
        intersect, then we will split/reposition the text_block so it accommodates the page break spacing
        """
        # handle when nothing to redact or we've reached the end of our list
        if not self.redacted_rects or redacted_rect_index >= len(self.redacted_rects):
            return 0, redacted_rect_index

        # if the bottom of the text block rect is above the current redacted rect
        if text_block_rect.y1 <= self.redacted_rects[redacted_rect_index].y0:
            return 0, redacted_rect_index

        redacted_offset = 0
        current_redacted_rect_index = redacted_rect_index
        # we add the y distance between the top and bottom of our redacted rect before progressing
        # to the next one, repeating as long as our current text block is below a redacted rect
        while text_block_rect.y0 > self.redacted_rects[current_redacted_rect_index].y1:
            redacted_offset += self.redacted_rects[current_redacted_rect_index].height
            current_redacted_rect_index += 1

            # terminates early if we get to the end of our list
            if current_redacted_rect_index == len(self.redacted_rects):
                break

        return redacted_offset, current_redacted_rect_index

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF into the number of pages found on our original template PDF
        """

        # unpacks template details dict values and checks if all are defined
        page_count, page_width, page_height = self.template_pdf_details.values()
        if not all((page_count, page_width, page_height)):
            # TODO Error Handling
            raise Exception

        tailored_resume = pymupdf.open()
        for page_number in range(0, page_count):
            page_offset_height = page_height * page_number
            unified_page_rect = pymupdf.Rect(
                0,
                0 + page_offset_height,
                page_width,
                page_height + page_offset_height
            )

            resume_page = tailored_resume.new_page(
                -1,
                width=page_width,
                height=page_height
            )

            resume_page.show_pdf_page(
                resume_page.rect,
                unified_pdf,
                clip=unified_page_rect
            )

        # TODO remove any blank pages
        return tailored_resume

    def calculate_updated_rect(self, text_block, offset_by):
        """
        This function is meant to use our self.page_break_rects to reposition the rect passed in
        if it falls into one of the rects that capture our footer + header spacing. If it does
        intersect, then we will split/reposition the text_block so it accommodates the page break spacing
        """
        updated_rect = self._get_rect(text_block, offset_by)

        # check if updated rectangle intersects with a page break
        for page_break_rect in self.page_break_rects:
            if not page_break_rect.intersects(updated_rect):
                continue

            # TODO break up only part of text block that overlaps
            updated_offset = offset_by + page_break_rect.height
            updated_rect = self._get_rect(text_block, updated_offset)
            break

        return updated_rect

    def extend_borders_to_width(self, bullet_rect):
        # TODO account for multiple columns
        left_of_page, right_of_page = 0, self.template_pdf_details["width"]
        bullet_rect.x0 = left_of_page
        bullet_rect.x1 = right_of_page

        return bullet_rect

    def isolate_repositioned_rect(self, repositioned_rect, redacted_pdf, template_rect):
        """
        This function takes our repositioned text block from the template resume and copies that Rect onto a
        temporary PDF. Because pymupdf's show_pdf_page will also copy all text, links, and annotations on the page,
        not just the text inside the Rect (See: https://pymupdf.readthedocs.io/en/latest/page.html#Page.show_pdf_page)
        we need to annotate all the space around our repositioned text block and redact it to remove all extraneous
        text/links. We then return the temporary PDF page with only the text block.
        """
        interim_pdf_unified = self._generate_unified_pdf(*self.template_pdf_details.values())
        interim_page_unified = interim_pdf_unified[0]

        interim_page_unified.show_pdf_page(
            repositioned_rect,
            redacted_pdf,
            clip=template_rect
        )

        page_rect = interim_page_unified.rect

        # redact everything else by creating four Rects around our rect and redacting everything around it
        rect_above_repositioned_rect = self._get_rect([
            page_rect.x0,  # Leftmost part of Page
            page_rect.y0,  # Top of Page
            page_rect.x1,  # Rightmost part of Page
            repositioned_rect.y0  # Top of repositioned rect
        ])

        rect_left_of_repositioned_rect = self._get_rect([
            page_rect.x0,  # Leftmost part of Page
            repositioned_rect.y0,  # Top of repositioned rect
            repositioned_rect.x0,  # Leftmost part of repositioned rect
            repositioned_rect.y1  # Bottom of repositioned rect
        ])

        rect_right_of_repositioned_rect = self._get_rect([
            repositioned_rect.x1,  # Rightmost part of repositioned rect
            repositioned_rect.y0,  # Top of repositioned rect
            page_rect.x1,  # Rightmost part of Page
            repositioned_rect.y1  # Bottom of repositioned rect
        ])

        rect_below_repositioned_rect = self._get_rect([
            page_rect.x0,  # Leftmost part of Page
            repositioned_rect.y1,  # Bottom of repositioned rect
            page_rect.x1,  # Rightmost part of Page
            page_rect.y1  # Bottom of page
        ])

        for redact_rect in (
                rect_above_repositioned_rect,
                rect_left_of_repositioned_rect,
                rect_right_of_repositioned_rect,
                rect_below_repositioned_rect
        ):
            interim_page_unified.add_redact_annot(redact_rect)

        interim_page_unified.apply_redactions()
        interim_pdf_unified.reload_page(interim_page_unified)
        return interim_pdf_unified

    def _combine_rects(self, rect_list=[]):
        if not rect_list:
            return None

        page_count, page_width, page_height = self.template_pdf_details.values()

        leftmost_x = page_width
        topmost_y = page_height * page_count
        rightmost_x = 0
        bottommost_y = 0

        for rect in rect_list:
            leftmost_x = min(leftmost_x, rect.x0)
            topmost_y = min(topmost_y, rect.y0)
            rightmost_x = max(rightmost_x, rect.x1)
            bottommost_y = max(bottommost_y, rect.y1)

        combined_rect = pymupdf.Rect(leftmost_x, topmost_y, rightmost_x, bottommost_y)

        if not combined_rect.is_valid or combined_rect.is_empty:
            return None

        # extend to rectangle X coordinates to capture bullet symbol and \n line
        combined_rect = self.extend_borders_to_width(combined_rect)
        return combined_rect

    @staticmethod
    def _get_rect(block, offset=0):
        rect = pymupdf.Rect(block[0], block[1] - offset, block[2], block[3] - offset)
        if not rect.is_valid or rect.is_empty:
            raise KeyError("generated_rect is invalid")
        return rect

    @staticmethod
    def _generate_unified_pdf(page_count, page_width, page_height):
        new_pdf = pymupdf.open()
        new_pdf.new_page(width=page_width, height=page_height * page_count)
        return new_pdf
