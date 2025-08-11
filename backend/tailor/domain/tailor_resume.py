import pymupdf

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
        self.bullet_symbol = None
        self.redacted_rects = []
        self.page_break_rects = []
        self.tailored_resume_in_bytes = self.tailor_pdf_in_bytes(bullets_to_redact)

    def tailor_pdf_in_bytes(self, bullets_to_redact):
        # TODO better to create the single page pdf and identify columns/header spacing when first uploaded
        try:
            template_pdf_unified = self.generate_unified_pdf()
            print("made it to redact bullets")

            redacted_pdf_unified = self.redact_bullets_from_pdf(bullets_to_redact, template_pdf_unified)
            tailored_pdf_unified = self.format_tailored_pdf_unified(redacted_pdf_unified)

            print("made it to split unified pdf")
            tailored_resume = self.split_unified_pdf(tailored_pdf_unified)
            print("made it out of split unified pdf")

            print("made it to split  into bytes")
            tailored_resume_in_bytes = tailored_resume.tobytes()
            print(tailored_resume_in_bytes)
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

        self.template_pdf_details = {
            "page_count": template_pdf.page_count,
            "width": template_pdf[0].rect.width,
            "height": template_pdf[0].rect.height
        }

        if not all(list(self.template_pdf_details.values())):
            # TODO Error Handling
            raise KeyError("error when attempting to calculate template pdf dimensions")

        # creates unified pdf with one page that is as long as there are pages in our template pdf
        template_pdf_unified = pymupdf.open()
        template_pdf_page_unified = template_pdf_unified.new_page(
            width=self.template_pdf_details["width"],
            height=self.template_pdf_details["height"] * self.template_pdf_details["page_count"]
        )

        header_from_this_page = None
        footer_from_previous_page = None

        # Maps template pages onto unified pdf
        for page in template_pdf:
            # determines how many pages we've already added/need to account for
            page_offset_height = self.template_pdf_details["height"] * page.number

            updated_top_of_page = page.rect.y0 + page_offset_height
            updated_bottom_of_page = page.rect.y1 + page_offset_height

            location_on_unified_pdf = pymupdf.Rect(
                page.rect.x0,
                updated_top_of_page,
                page.rect.x1,
                updated_bottom_of_page)

            template_pdf_page_unified.show_pdf_page(location_on_unified_pdf, template_pdf, page.number)

            # calculates page break spacing on unified pdf (if applicable)
            header_height, footer_height = self.calculate_page_break_spacing(page)
            header_from_this_page = updated_top_of_page + header_height

            # checks if we already have a footer from the previous page and can calculate the combined volume
            if footer_from_previous_page and footer_from_previous_page < header_from_this_page:
                rect = pymupdf.Rect(0, footer_from_previous_page, self.template_pdf_details["width"], header_from_this_page)
                self.page_break_rects.append(rect)

            footer_from_previous_page = updated_bottom_of_page - footer_height

        return template_pdf_unified

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF into the number of pages found on our original template PDF
        """
        # unpacks template details dict values and checks if all are defined
        if not all(list(self.template_pdf_details.values())):
            # TODO Error Handling
            raise Exception

        tailored_resume = pymupdf.open()

        for page_number in range(0, self.template_pdf_details["page_count"]):
            page_offset_height = self.template_pdf_details["height"] * page_number
            unified_page_rect = pymupdf.Rect(
                0,
                0 + page_offset_height,
                self.template_pdf_details["width"],
                self.template_pdf_details["height"] + page_offset_height
            )

            resume_page = tailored_resume.new_page(
                -1,
                width=self.template_pdf_details["width"],
                height=self.template_pdf_details["height"]
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
        # print(bullets_to_redact)

        self.redacted_rects = self.calculate_redacted_rects(bullets_to_redact, template_page)
        print(self.redacted_rects)

        for redacted_rect in self.redacted_rects:
            template_page.add_redact_annot(redacted_rect)

        result = template_page.apply_redactions()
        if not result:
            # TODO error handling
            print("could not find any bullets on the page")

        template_pdf.reload_page(template_page)
        return template_pdf

    def calculate_redacted_rects(self, bullets_to_redact, template_page):
        redacted_rects = [self._combine_rects_list(template_page.search_for(bullet)) for bullet in bullets_to_redact]
        filtered_redacted_rects = [rect for rect in redacted_rects if rect is not None]
        # TODO remove this once we get the OpenAI response figured out
        sorted_redacted_rects = sorted(filtered_redacted_rects, key=lambda redacted_rect: redacted_rect.y0)

        return sorted_redacted_rects


    def format_tailored_pdf_unified(self, redacted_pdf: pymupdf.Document):
        print("made it to tailoring pdf")
        redacted_page = redacted_pdf[0]

        tailored_pdf_unified = pymupdf.open()
        tailored_pdf_unified.new_page(
            width=self.template_pdf_details["width"],
            height=self.template_pdf_details["height"] * self.template_pdf_details["page_count"]
        )

        tailored_page_unified = tailored_pdf_unified[0]

        redacted_index = 0
        total_offset_by = 0
        for text_block in redacted_page.get_text("blocks"):
            template_rect = self._get_rect(text_block)

            # handle when nothing to redact or we've redacted everything
            if self.redacted_rects and redacted_index < len(self.redacted_rects):
                redacted_offset = 0
                print("–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––")
                print("made it to template rect comparison")
                print("template_rect.y0")
                while template_rect.y0 > self.redacted_rects[redacted_index].y0:
                    redacted_rect = self.redacted_rects[redacted_index]
                    redacted_offset += redacted_rect.height + self.line_break_offset
                    redacted_index += 1

                total_offset_by += redacted_offset
                if template_rect.y0 > redacted_rect.y1:
                    print(f"textblock: {text_block}")

                    print(f" offset is : {total_offset_by}")

                    print(f"template rect is : {template_rect.y0}")
                    print(f"redacted rect is : {redacted_rect.y1}")

                    # y distance between top of first line of redacted text and bottom of last line of redacted text
                    redacted_offset = redacted_rect.height

                    print(f"height offset is : {redacted_offset}")

                    # y distance between the last line of the redacted text and the first line of the non-redacted text
                    line_break_offset = template_rect.y0 - redacted_rect.y1
                    print(f"line break offset is : {line_break_offset}")

                    # TODO handle two column offset
                    total_offset_by += redacted_offset + line_break_offset
                    redacted_index += 1

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
            repositioned_rect = self.calculate_updated_rect(text_block, total_offset_by)
            # print("made it out of repositing")
            # print(repositioned_rect)

            interim_pdf_unified = self.isolate_repositioned_rect(repositioned_rect, redacted_pdf, template_rect)

            tailored_page_unified.show_pdf_page(
                repositioned_rect,
                interim_pdf_unified,
                clip=repositioned_rect
            )

            interim_pdf_unified.close()

        return tailored_pdf_unified

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

    def isolate_repositioned_rect(self, repositioned_rect, redacted_pdf, template_rect):
        """
        This function takes our repositioned text block from the template resume and copies that Rect onto a
        temporary PDF. Because pymupdf's show_pdf_page will also copy all text, links, and annotations on the page,
        not just the text inside the Rect (See Note: https://pymupdf.readthedocs.io/en/latest/page.html#Page.show_pdf_page)
        we need to annotate all the space around our repositioned text block and redact it to remove all extraneous
        text/links. We then return the temporary PDF with only the text block.
        """

        interim_pdf_unified = pymupdf.open()
        interim_pdf_unified.new_page(
            width=self.template_pdf_details["width"],
            height=self.template_pdf_details["height"] * self.template_pdf_details["page_count"]
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

    def _combine_rects_list(self, rect_list=[]):
        if not rect_list:
            return None

        leftmost_x = self.template_pdf_details["width"]
        topmost_y = self.template_pdf_details["height"] * self.template_pdf_details["page_count"]
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
        return pymupdf.Rect(block[0], block[1] - offset, block[2], block[3] - offset)
