import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict
import pymupdf


class TailorPdf:
    def __init__(self, template_resume, bullets_to_redact):
        self.template_resume = template_resume
        self.tailored_resume = None
        self.bullets_to_redact = bullets_to_redact
        self.template_pdf_details = {
            "page_count": 0,
            "width": 0,
            "height": 0,
        }
        self.unified_template_page = None
        self.redacted_rects = []
        self.column_data = {}
        self.page_break_rects = []

    def create_tailored_resume(self):
        try:
            self.generate_unified_pdf()
            self.calculate_spacing()
            self.redact_bullets_from_pdf()

            tailored_pdf_unified = self.format_tailored_pdf_unified()

            self.tailored_resume = self.split_unified_pdf(tailored_pdf_unified)
            return
        except Exception as e:
            print(f"error: {e}")
            return e

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
        unified_template_pdf = self._generate_unified_pdf()
        unified_template_page = unified_template_pdf[0]

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

            unified_template_page.show_pdf_page(location_on_unified_pdf, template_pdf, page.number)

        self.unified_template_page = unified_template_page
        return

    def calculate_spacing(self):
        template_page = self.unified_template_page
        self.column_data = self.calculate_column_data(template_page)
        self.page_break_rects = self.calculate_page_break_spacing(template_page)
        return

    def calculate_column_data(self, template_page_unified: pymupdf.Page):
        """
        returns a dictionary of identified columns in the document using the DBSCAN clustering method.
        DBSCAN will take an array, in this case the horizontal(X coordinate) bounds of each text block in the resume,
        and identify groups of clusters. If a text block is not grouped, then it will be given
        a cluster label of -1. Sorting our text blocks by cluster label, we will then create a rect that encapsulates
        all the text blocks for a given cluster rect. This will allow us to identify later if a bullet we
        are redacting/repositioning is in a column that should be offset.

        see: https://inria.hal.science/hal-04668648/document
             https://github.com/pymupdf/PyMuPDF/discussions/2259
             https://medium.com/@sachinsoni600517/clustering-like-a-pro-a-beginners-guide-to-dbscan-6c8274c362c4


        data structure:

        column_data :{
            cluster_id: {
                rect: [],
                offset: 0
            },
            ...
        }

        TODO: Determine if we need to worry about footer text in resumes; if not, extend column rects to floor
        TODO: Determine if we should calculate column spacing for each page
        """

        text_blocks = template_page_unified.get_text("blocks")
        X = np.array(
            [(x0, x1) for x0, y0, x1, y1, text, block_no, block_type in text_blocks]
        )
        # TODO improve calculation for epsilon
        dbscan = DBSCAN(eps=self.template_pdf_details["width"]//6)
        dbscan.fit(X)
        cluster_labels = dbscan.labels_

        # using defaultdict so we don't check need to check for the key when appending
        column_clusters = defaultdict(list)
        for i in range(len(text_blocks)):
            text_block, text_block_cluster_no = text_blocks[i], cluster_labels[i]
            column_clusters[text_block_cluster_no].append(text_block)

        column_data = {}
        for column_cluster_no, column_cluster_blocks in column_clusters.items():
            if column_cluster_no == -1:  # skip outliers
                continue

            column_data[column_cluster_no] = {
                "rect": self._combine_rects(column_cluster_blocks),
                "offset": 0
            }

        # include entire page dimensions if only one column
        if len(column_data) == 1:
            column_data[0]["rect"] = self.unified_template_page.rect

        return column_data

    def calculate_page_break_spacing(self, template_page_unified: pymupdf.Page):
        """
        returns a list of page_break_rects that span from the bottom of text on a previous page (top of footer)
        to the top of text on the current page (bottom of header)
        """
        page_count, page_width, page_height = self.template_pdf_details.values()

        # points in our unified pdf where we cross into a new page
        page_break_heights = [page_height * i for i in range(1, page_count + 1)]
        page_break_index = 0
        page_break_rects = []

        # return early if only one-page resume
        if page_count == 1:
            return page_break_rects

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

    def redact_bullets_from_pdf(self):
        """
        Identifies where in the page our bullets are that we want to delete, saves the location of where they were
        as a Rect (including the line break spacing between them and the next bullet point), and then redacts them
        """
        template_page = self.unified_template_page

        for bullet in self.bullets_to_redact:
            rects_containing_bullet = template_page.search_for(bullet)
            redacted_rect = self._combine_rects(rects_containing_bullet)

            if redacted_rect is None:
                # TODO log that we couldnt find bullet point
                continue

            self.format_redacted_rect(redacted_rect)

            self.redacted_rects.append(redacted_rect)
            template_page.add_redact_annot(redacted_rect)

        # TODO remove once OpenAI Response is correctly sorting the bullet points
        # TODO account for column
        self.redacted_rects = sorted(self.redacted_rects, key=lambda rect: rect.y0)

        result = template_page.apply_redactions()
        if not result:
            raise ValueError("No redactions applied")
        return

    def format_redacted_rect(self, redacted_rect: pymupdf.Rect):
        self.fit_borders_to_column(redacted_rect)
        self.maybe_fit_height_to_bullet(redacted_rect)
        self.maybe_add_line_break(redacted_rect)

    def fit_borders_to_column(self, redacted_rect: pymupdf.Rect):
        """
        This will extend the X borders of our rect to either the column that it is located in, or to
        the width of the page if there is only one column. This will account for bullet symbols (e.g. "-") and \n
        """

        column_id = self._get_column_id(redacted_rect)
        if column_id is not None:
            redacted_rect.x0 = self.column_data[column_id]["rect"].x0
            redacted_rect.x1 = self.column_data[column_id]["rect"].x1
            return

        raise ValueError("Unable to find rect in column")

    def maybe_fit_height_to_bullet(self, redacted_rect):
        """
        It's possible that the bullet symbol to the left of our text has a rect that is slightly above or
        below our text rect, which will affect the drift of repositioning on the page unless addressed.
        Now that's we've extended our rect borders to the width, we should be able to capture any bullet symbols
        with get_textbox and reconfigure the height

        TODO make sure this doesn't break with two-column spacing
        """
        text_including_bullet = self.unified_template_page.get_textbox(redacted_rect)
        text_including_bullet_rects = self.unified_template_page.search_for(text_including_bullet)
        text_including_bullet_combined_rect = self._combine_rects(text_including_bullet_rects)

        redacted_rect.y0 = min(redacted_rect.y0, text_including_bullet_combined_rect.y0)
        redacted_rect.y1 = max(redacted_rect.y1, text_including_bullet_combined_rect.y1)

    def maybe_add_line_break(self, redacted_rect: pymupdf.Rect):
        """
        This function checks if we can find any text below our redacted rect. If so, we will calculate
        the empty space between them before extending the redacted rect to cover this whitespace. This
        will allow us to account for it later when we are repositioning the text below it.
        If we do not find any text below our redacted rect, we return the redacted rect as is

        TODO ensure that we are only checking one lines worth and are not accidentally hitting the next job experience
        TODO verify that this approach works for most resumes (i.e. bullet line spacing is < the height of a bullet point)
        """

        # use a negative offset to generate a rect of the same size underneath and the +1 to avoid intersection
        offset_by_redacted_rect = -1 * (redacted_rect.height + 1)
        rect_underneath_redacted_rect = self._get_rect(redacted_rect, offset_by_redacted_rect)
        text_underneath_redacted_rect = self.unified_template_page.get_textbox(rect_underneath_redacted_rect)
        if not text_underneath_redacted_rect.strip():  # checks if there is only whitespace
            return

        # TODO verify that we won't encounter duplicate text that could be present elsewhere
        # by rebuilding our rect by searching for the text we found, we can ensure we are not including the line
        # break spacing between our redacted rect and this text just below it.
        nearest_rect_containing_text = self.unified_template_page.search_for(text_underneath_redacted_rect)[0]

        # stretch the bottom of our redacted rect to just above our text_rect to include line break spacing
        if nearest_rect_containing_text and not nearest_rect_containing_text.intersects(redacted_rect):
            redacted_rect.y1 = nearest_rect_containing_text.y0

        return

    def format_tailored_pdf_unified(self):
        """
        This function repositions the remaining text on our redacted pdf onto a new pdf using the location of our
        redacted rects to determine how much we are moving the repositioned text up by.
        """
        redacted_page = self.unified_template_page

        tailored_pdf_unified = self._generate_unified_pdf()
        tailored_page_unified = tailored_pdf_unified[0]

        redacted_rect_index = 0
        for text_block in redacted_page.get_text("blocks"):
            text_rect = self._get_rect(text_block)

            text_offset = 0
            column_id = self._get_column_id(text_rect)
            if column_id is not None:
                redacted_offset, redacted_rect_index = self.calculate_text_rect_offset(redacted_rect_index, text_rect)

                column = self.column_data[column_id]
                current_column_offset = column["offset"]

                text_rect_with_redacted_offset = self._get_rect(text_block, current_column_offset + redacted_offset)
                page_break_offset = self.maybe_correct_for_page_break(text_rect_with_redacted_offset)

                corrected_offset = redacted_offset - page_break_offset
                column = self.column_data[column_id]
                column["offset"] += corrected_offset
                text_offset = column["offset"]

            repositioned_text_rect = self._get_rect(text_block, text_offset)

            if self.out_of_bounds(repositioned_text_rect):
                raise ValueError("Should not get a rect position that is outside our unified pdf")

            interim_pdf_unified = self.isolate_repositioned_rect(repositioned_text_rect, redacted_page.parent, text_rect)

            tailored_page_unified.show_pdf_page(
                repositioned_text_rect,
                interim_pdf_unified,
                clip=repositioned_text_rect
            )

            interim_pdf_unified.close()

        redacted_page.parent.close()
        return tailored_pdf_unified

    def calculate_text_rect_offset(self, redacted_rect_index: int, text_block_rect: pymupdf.Rect):
        """
        Here we calculate if the text_block_rect we are evaluating is below the redacted_rect located at our index.
        If it is, then text_block_rect is the next available text_block after our redactions, which means that we could
        have jumped over multiple redactions to get there.
        Example:
        Page before redaction
        - A
        - B
        - C
        - D
        Page after redaction
        - A
             <- B has been redacted
             <- C has been redacted
        - D  <- needs to be repositioned on the new pdf by the height of B + C
        Tailored PDF
        - A
        - D
        This means we need to keep stepping along our redacted_rect list until our text_block_rect is no longer
        below a redacted_rect or we have run through all of our redacted_rects
        """
        # return early if reached the end of redacted rect list
        if not self.redacted_rects or redacted_rect_index >= len(self.redacted_rects):
            return 0, redacted_rect_index

        redacted_rect = self.redacted_rects[redacted_rect_index]
        text_column, redacted_column = self._get_column_id(text_block_rect), self._get_column_id(redacted_rect)

        # return if columns are not aligned
        if text_column != redacted_column:
            return 0, redacted_rect_index

        # return if the bottom of the text block rect is above the current redacted rect
        if text_block_rect.y1 <= redacted_rect.y0:
            return 0, redacted_rect_index

        redacted_offset = 0
        current_redacted_rect_index = redacted_rect_index
        # we add the y distance between the top and bottom of our redacted rect before progressing
        # to the next one, repeating as long as our current text block is below a redacted rect in the same column
        while text_block_rect.y0 >= self.redacted_rects[current_redacted_rect_index].y0:

            redacted_offset += self.redacted_rects[current_redacted_rect_index].height
            current_redacted_rect_index += 1

            # terminates early if we get to the end of our list
            if current_redacted_rect_index == len(self.redacted_rects):
                break

            # terminates if columns no longer match
            next_redacted_rect = self.redacted_rects[current_redacted_rect_index]
            redacted_column = self._get_column_id(next_redacted_rect)
            if text_column != redacted_column:
                break

        return redacted_offset, current_redacted_rect_index

    def maybe_correct_for_page_break(self, rect: pymupdf.Rect):
        """
        Here are the rules:
        1. If it is not intersecting with any page break then return 0 and continue as normal
        2. If only the bottom of the rect is intersecting with the top of the page break:
            break text_block into overlapping lines
            we need to move the rect down by the height of the page break, plus the height of the rect
            not currently overlapping (since it will be sticking up into the page break once we move it down)
            return page_break + non-overlap amount (page_break.y0 - rect.y0))
        3. Otherwise the top or the entire rect is intersecting with the bottom of the page break:
            we need to move the rect down by the bottom of the page break
            return overlap amount (page_break.y1- rect.y0)

            # TODO For scenario 2: right now we are shunting down the entire text_block even if its only one line over
            # TODO future versions should consider splitting off the offending line and offseting by only that much
        """
        overlapping_page_break = None
        for page_break in self.page_break_rects:
            if page_break.intersects(rect):
                overlapping_page_break = page_break
                break

        if not overlapping_page_break:
            return 0

        # bottom of rect overlapping footer
        if rect.y0 < overlapping_page_break.y0:
            distance_from_top_of_rect_to_top_of_footer = overlapping_page_break.y0 - rect.y0
            return overlapping_page_break.height + distance_from_top_of_rect_to_top_of_footer
        else: # top of rect overlapping header or entire rect in page_break
            distance_from_top_of_rect_to_bottom_of_header = overlapping_page_break.y1 - rect.y0
            return distance_from_top_of_rect_to_bottom_of_header

    def isolate_repositioned_rect(self, repositioned_rect, redacted_pdf, template_rect):
        """
        This function takes our repositioned text block from the template resume and copies that Rect onto a
        temporary PDF. Because pymupdf's show_pdf_page will also copy all text, links, and annotations on the page,
        not just the text inside the Rect (See: https://pymupdf.readthedocs.io/en/latest/page.html#Page.show_pdf_page)
        we need to annotate all the space around our repositioned text block and redact it to remove all extraneous
        text/links. We then return the temporary PDF page with only the text block.
        """
        interim_pdf_unified = self._generate_unified_pdf()
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
        interim_page_unified.clean_contents()
        interim_pdf_unified.reload_page(interim_page_unified)
        return interim_pdf_unified

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF into the number of pages found on our original template PDF
        """
        page_count, page_width, page_height = self.template_pdf_details.values()

        tailored_resume = pymupdf.open()
        for page_number in range(0, page_count):
            page_offset_height = page_height * page_number
            unified_page_rect = pymupdf.Rect(
                0,
                0 + page_offset_height,
                page_width,
                page_height + page_offset_height
            )

            # Don't add page if no text present
            text_on_page = unified_pdf[0].get_textbox(unified_page_rect)
            if not text_on_page.strip():
                continue

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

        return tailored_resume

    def out_of_bounds(self, rect):
        return not self.unified_template_page.rect.contains(rect)

    def _generate_unified_pdf(self):
        page_count, page_width, page_height = self.template_pdf_details.values()
        new_pdf = pymupdf.open()
        new_pdf.new_page(width=page_width, height=page_height * page_count)
        return new_pdf

    def _get_column_id(self, rect: pymupdf.Rect):
        column_id = None

        for col_id, column in self.column_data.items():
            if column["rect"].contains(rect):
                column_id = col_id
                break

        #TODO raise error or None if found in all
        return column_id

    @staticmethod
    def _get_rect(block, offset=0):
        try:
            rect = pymupdf.Rect(block[0], block[1] - offset, block[2], block[3] - offset)
            if not rect.is_valid or rect.is_empty:
                raise ValueError("Rect is empty or invalid")
            return rect
        except (IndexError, AssertionError, TypeError):
            raise ValueError("Invalid parameters when generating Rect")

    def _combine_rects(self, rect_list):
        if not rect_list:
            return None

        page_count, page_width, page_height = self.template_pdf_details.values()

        leftmost_x = page_width
        topmost_y = page_height * page_count
        rightmost_x = 0
        bottommost_y = 0

        for item in rect_list:
            rect = self._get_rect(item) if not isinstance(item, pymupdf.Rect) else item

            leftmost_x = min(leftmost_x, rect.x0)
            topmost_y = min(topmost_y, rect.y0)
            rightmost_x = max(rightmost_x, rect.x1)
            bottommost_y = max(bottommost_y, rect.y1)

        combined_rect = pymupdf.Rect(leftmost_x, topmost_y, rightmost_x, bottommost_y)

        if not combined_rect.is_valid or combined_rect.is_empty:
            raise ValueError("Unable to generate a valid combined rect")

        return combined_rect

    def tailor_pdf_in_bytes(self):
        tailored_resume = self.tailored_resume
        tailored_resume.subset_fonts()
        return tailored_resume.tobytes(garbage=3, deflate=True, use_objstms=1)

