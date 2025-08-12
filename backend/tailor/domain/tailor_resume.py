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
        # TODO better to create the single page pdf and identify columns/header spacing when first uploaded
        try:
            template_pdf_unified = self.generate_unified_pdf()
            self.page_break_rects = self.calculate_page_break_spacing(template_pdf_unified[0])
            redacted_pdf_unified = self.redact_bullets_from_pdf(bullets_to_redact, template_pdf_unified)
            tailored_pdf_unified = self.format_tailored_pdf_unified(redacted_pdf_unified)

            tailored_resume = self.split_unified_pdf(tailored_pdf_unified)

            print("made it to split  into bytes")
            tailored_resume_in_bytes = tailored_resume.tobytes()
            print("made it out of bytes")

            # template_pdf_unified.close()
            # tailored_pdf_unified.close()
            # # tailored_resume.close()

            return tailored_resume_in_bytes
        # TODO add error handling
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
        template_pdf_unified = pymupdf.open()
        template_pdf_page_unified = template_pdf_unified.new_page(
            width=page_width,
            height=page_height * page_count
        )

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

    def redact_bullets_from_pdf(self, bullets_to_redact: [], template_pdf: pymupdf.Document):
        template_page = template_pdf[0]

        for bullet in bullets_to_redact:
            redacted_text_rect = self._combine_rects(template_page.search_for(bullet))

            if not redacted_text_rect:
                continue

            rect_below_redacted_text = self._get_rect(list(redacted_text_rect), redacted_text_rect.height * -1)
            text_below_redacted = template_page.get_textbox(rect_below_redacted_text)
            text_rect_below_redacted = self._combine_rects(template_page.search_for(text_below_redacted))

            if text_rect_below_redacted and not text_rect_below_redacted.intersects(redacted_text_rect):
                print(f"redacted rect before {redacted_text_rect}")
                print(f"get text: {template_page.get_textbox(redacted_text_rect)}")
                print("––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––")

                print(f"distance from redacted rect floor to text_rect_below_redacted ceiling {text_rect_below_redacted.y0 - redacted_text_rect.y1 } ")

                print("––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––")
                redacted_text_rect = self._get_rect([
                    redacted_text_rect.x0,
                    redacted_text_rect.y0,
                    redacted_text_rect.x1,
                    text_rect_below_redacted.y0 - 0.000001
                ])
                print(f"redacted rect after {redacted_text_rect}")
                # print(f"get text: {template_page.get_textbox(redacted_text_rect)}")

            self.redacted_rects.append(redacted_text_rect)
        self.redacted_rects = sorted(self.redacted_rects, key=lambda rect: rect.y0)



        # calculated_redacted_rects = [
        #     # Page.search_for() returns a list of all Rects where our bullet point is found,
        #     # we then combine this list into one large Rect using our combine_rects method
        #     self._combine_rects(template_page.search_for(bullet)) for bullet in bullets_to_redact
        # ]
        # filtered_redacted_rects = [rect for rect in calculated_redacted_rects if rect is not None]
        # # TODO remove this once we get the OpenAI response figured out
        # self.redacted_rects = sorted(filtered_redacted_rects, key=lambda rect: rect.y0)
        #
        # redacted_line_breaks = []
        for redacted_rect in self.redacted_rects:
            # adjacent_line_break = self.measure_bullet_line_break(redacted_rect, template_page)
            # if adjacent_line_break:
            #     redacted_line_breaks.append(adjacent_line_break)

            template_page.add_redact_annot(redacted_rect)

        # self.bullet_line_break = mode(redacted_line_breaks)[0]
        # print(f"bullet_line_break is {self.bullet_line_break}")

        result = template_page.apply_redactions()
        if not result:
            # TODO error handling
            print("could not find any bullets on the page")

        template_pdf.reload_page(template_page)
        return template_pdf

    def format_tailored_pdf_unified(self, redacted_pdf: pymupdf.Document):
        print("made it to tailoring pdf")
        redacted_page = redacted_pdf[0]
        page_count, page_width, page_height = self.template_pdf_details.values()


        tailored_pdf_unified = pymupdf.open()
        tailored_pdf_unified.new_page(
            width=page_width,
            height=page_height * page_count
        )

        tailored_page_unified = tailored_pdf_unified[0]

        redacted_index = 0
        total_offset_by = 0
        for text_block in redacted_page.get_text("blocks"):
            text_block_rect = self._get_rect(text_block)

            redacted_offset, redacted_index = self.calculate_rect_offset(redacted_index, text_block_rect)
            total_offset_by += redacted_offset

            repositioned_rect = self.calculate_updated_rect(text_block, total_offset_by)
            interim_pdf_unified = self.isolate_repositioned_rect(repositioned_rect, redacted_pdf, text_block_rect)

            tailored_page_unified.show_pdf_page(
                repositioned_rect,
                interim_pdf_unified,
                clip=repositioned_rect
            )

            interim_pdf_unified.close()

        return tailored_pdf_unified

    def calculate_rect_offset(self, redacted_index: int, text_block_rect: pymupdf.Rect):

        # handle when nothing to redact or we've reached the end of our list
        if not self.redacted_rects or redacted_index >= len(self.redacted_rects):
            return 0, redacted_index

        # if the bottom of the text block rect is above the current redacted rect
        if text_block_rect.y1 <= self.redacted_rects[redacted_index].y0:
            return 0, redacted_index

        # continue looping until redacted_rects[redacted_index] rect is below our text_block
        redacted_offset = 0
        updated_index = redacted_index
        while text_block_rect.y0 > self.redacted_rects[updated_index].y1:

            # # y distance between the last line of the redacted text and the first line of the non-redacted text
            # line_break_offset = text_block_rect.y0 - self.redacted_rects[updated_index].y1

            # y distance between top of first line of redacted text and bottom of last line of redacted text
            # print(f"line break offset is {self.bullet_line_break}")
            # redacted_offset += self.redacted_rects[updated_index].height + self.bullet_line_break
            redacted_offset += self.redacted_rects[updated_index].height
            updated_index += 1

            # terminates if we get to the end of our list
            if updated_index == len(self.redacted_rects):
                break

        # print(f"textblock: {text_block}")
        #
        #         print(f" offset is : {total_offset_by}")
        #
        #         print(f"template rect is : {text_block_rect.y0}")
        #         print(f"redacted rect is : {redacted_rect.y1}")
        # print("made it to repositing")
        #
        # print("redacted info")
        # print(redacted_index)
        # print(len(self.redacted_rects))
        #
        # print("page info")
        # print(tailored_page_unified.rect)
        # print("block info")
        # print(text_block)
        # print(offset_by)
        # print("made it out of repositing")
        # print(repositioned_rect)

        print(f"redacted offset is {redacted_offset}")
        return redacted_offset, updated_index

    def calculate_updated_rect(self, text_block, offset_by):
        updated_rect = self._get_rect(text_block, offset_by)

        # check if updated rectangle intersects with a page break
        for page_break_rect in self.page_break_rects:
            # print(page_break_rect)
            if not page_break_rect.intersects(updated_rect):
                continue

            print(page_break_rect)
            print("rect intersects")
            print(updated_rect)
            # TODO break up only part of text block that overlaps
            updated_offset = offset_by + page_break_rect.height
            updated_rect = self._get_rect(text_block, updated_offset)
            print("new rect is")
            print(updated_rect)
            break

        return updated_rect

    def extend_borders_to_width(self, bullet_rect):
        # TODO accommodate for multiple columns
        left_of_page, right_of_page = 0, self.template_pdf_details["width"]
        bullet_rect.x0 = left_of_page
        bullet_rect.x1 = right_of_page

        return bullet_rect

    def measure_bullet_line_break(self, redacted_rect, template_page):
        redacted_height = redacted_rect.height

        rect_above_redacted = self._get_rect(list(redacted_rect), redacted_height+2)
        text_above_redacted = template_page.get_textbox(rect_above_redacted)
        text_rect_above_redacted = self._combine_rects(template_page.search_for(text_above_redacted))
        if text_rect_above_redacted and not text_rect_above_redacted.intersects(redacted_rect):
            line_break_above_redacted = redacted_rect.y0 - text_rect_above_redacted.y1
        else:
            line_break_above_redacted = float('inf')

        rect_below_redacted = self._get_rect(list(redacted_rect), redacted_height * -1)
        text_below_redacted = template_page.get_textbox(rect_below_redacted)
        text_rect_below_redacted = self._combine_rects(template_page.search_for(text_below_redacted))
        if text_rect_below_redacted and not text_rect_below_redacted.intersects(redacted_rect):
            line_break_below_redacted = text_rect_below_redacted.y0 - redacted_rect.y1
        else:
            line_break_below_redacted = float('inf')

        smallest_line_break = min(line_break_above_redacted, line_break_below_redacted)

        return 0 if smallest_line_break == float('inf') else smallest_line_break

    def isolate_repositioned_rect(self, repositioned_rect, redacted_pdf, template_rect):
        """
        This function takes our repositioned text block from the template resume and copies that Rect onto a
        temporary PDF. Because pymupdf's show_pdf_page will also copy all text, links, and annotations on the page,
        not just the text inside the Rect (See: https://pymupdf.readthedocs.io/en/latest/page.html#Page.show_pdf_page)
        we need to annotate all the space around our repositioned text block and redact it to remove all extraneous
        text/links. We then return the temporary PDF page with only the text block.
        """
        page_count, page_width, page_height = self.template_pdf_details.values()

        interim_pdf_unified = pymupdf.open()
        interim_pdf_unified.new_page(
            width=page_width,
            height=page_height * page_count
        )
        interim_page_unified = interim_pdf_unified[0]

        interim_page_unified.show_pdf_page(
            repositioned_rect,
            redacted_pdf,
            clip=template_rect
        )

        # redact everything else
        page_rect = interim_page_unified.rect
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
            repositioned_rect.y1]  # Bottom of repositioned rect
        )

        rect_right_of_repositioned_rect = self._get_rect([
            repositioned_rect.x1,  # Rightmost part of repositioned rect
            repositioned_rect.y0,  # Top of repositioned rect
            page_rect.x1,  # Rightmost part of Page
            repositioned_rect.y1]  # Bottom of repositioned rect
        )

        rect_below_repositioned_rect = self._get_rect([
            page_rect.x0,  # Leftmost part of Page
            repositioned_rect.y1,  # Bottom of repositioned rect
            page_rect.x1,  # Rightmost part of Page
            page_rect.y1]  # Bottom of page
        )

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

    def calculate_page_break_spacing(self, template_page_unified: pymupdf.Page):
        """
        returns a list of page_break_rects that span from the bottom of text on a previous page (top of footer)
        to the top of text on the current page (bottom of header)
        """

        # Note: get_text("blocks") returns array of tuples in the form:
        # (x0, y0, x1, y1, "lines in the block", block_no, block_type)

        page_count, page_width, page_height = self.template_pdf_details.values()
        page_break_heights = [page_height * page_no for page_no in range(1, page_count + 1)]
        page_break_index = 0
        page_break_rects = []

        previous_text_rect = None
        for text_block in template_page_unified.get_text("blocks"):
            text_rect = self._get_rect(text_block)

            # If we don't have a previous text block or we've reached the end of our page_break_rects list
            if not previous_text_rect or page_break_index == len(page_break_heights):
                previous_text_rect = text_rect
                continue

            if text_rect.y0 > page_break_heights[page_break_index]:
                # Create a Rect that spans the distance between the previous text on the last page and the first
                # text on the current page
                page_break_x0 = 0
                page_break_y0 = previous_text_rect.y1
                page_break_x1 = page_width
                page_break_y1 = text_rect.y0
                page_break_rects.append(
                    self._get_rect([page_break_x0, page_break_y0, page_break_x1, page_break_y1])
                )

                page_break_index += 1

            previous_text_rect = text_rect

        return page_break_rects

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
