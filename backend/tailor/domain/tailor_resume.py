import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict
import pymupdf

class TailorPdf:
    def __init__(self, template_resume, bullets_to_redact):
        self.template_resume = template_resume
        self.bullets_to_redact = bullets_to_redact
        self.template_pdf_details = {
            "page_count": 0,
            "width": 0,
            "height": 0,
        }
        self.unified_template_page = None
        self.redacted_rects = []
        self.column_rects = []
        self.page_break_rects = []

    def tailor_pdf_in_bytes(self):
        try:
            template_pdf_unified = self.generate_unified_pdf()

            self.calculate_spacing(template_pdf_unified)

            redacted_pdf_unified = self.redact_bullets_from_pdf(template_pdf_unified)

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
        return unified_template_pdf

    def calculate_spacing(self, template_pdf_unified: pymupdf.Document):
        self.column_rects = self.calculate_column_rects(template_pdf_unified[0])

        self.page_break_rects = self.calculate_page_break_spacing(template_pdf_unified[0])

    def calculate_column_rects(self, template_page_unified: pymupdf.Page):
        """
        returns a list of rects of the identified columns in the document using the DBSCAN clustering method.
        DBSCAN will take our array, in this case the horizontal(X coordinate) bounds of each text block in the resume,
        and identify clusters of similarly grouped bounds. If a text block is not grouped, then it will be given
        a cluster label of -1. Sorting our text blocks by cluster label, we will then create a rect that encapsulates
        all the text blocks for a given cluster rect. This will allow us to identify later if a bullet we
        are redacting/repositioning is in a column that should be offset.

        see: https://inria.hal.science/hal-04668648/document
             https://github.com/pymupdf/PyMuPDF/discussions/2259
             https://medium.com/@sachinsoni600517/clustering-like-a-pro-a-beginners-guide-to-dbscan-6c8274c362c4

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

        column_clusters = defaultdict(list)
        for i in range(len(text_blocks)):
            text_block, text_block_cluster_no = text_blocks[i], cluster_labels[i]
            column_clusters[text_block_cluster_no].append(text_block)

        column_rects = []
        for column_cluster_no, column_cluster_blocks in column_clusters.items():
            if column_cluster_no == -1:  # skip outliers
                continue

            column_rects.append(self._combine_rects(column_cluster_blocks))

        # include entire page dimensions if only one column
        if len(column_rects) == 1:
            column_rects[0] = self.unified_template_page.rect

        return column_rects

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

    def redact_bullets_from_pdf(self, template_pdf: pymupdf.Document):
        """
        Identifies where in the page our bullets are that we want to delete, saves the location of where they were
        as a Rect (including the line break spacing between them and the next bullet point), and then redacts them
        """
        template_page = template_pdf[0]

        for bullet in self.bullets_to_redact:
            rects_containing_bullet = template_page.search_for(bullet)
            redacted_rect = self._combine_rects(rects_containing_bullet)

            if not redacted_rect:
                continue

            redacted_rect = self.format_redacted_rect(redacted_rect)

            self.redacted_rects.append(redacted_rect)
            template_page.add_redact_annot(redacted_rect)

        # TODO remove once OpenAI Response is correctly sorting the bullet points
        self.redacted_rects = sorted(self.redacted_rects, key=lambda rect: rect.y0)

        result = template_page.apply_redactions()
        if not result:
            # TODO error handling
            print("could not find any bullets on the page")

        # template_pdf.reload_page(template_page)
        return template_pdf

    def format_redacted_rect(self, redacted_rect: pymupdf.Rect):
        redacted_rect = self.fit_to_column(redacted_rect)
        redacted_rect = self.maybe_add_line_break(redacted_rect)
        return redacted_rect

    def fit_to_column(self, redacted_rect: pymupdf.Rect):
        """
        This will extend the X borders of our rect to either the column that it is located in, or to
        the width of the page if there is only one column. This will account for bullet symbols (e.g. "-") and \n
        """
        for column in self.column_rects:
            if column.contains(redacted_rect):
                redacted_rect.x0 = column.x0
                redacted_rect.x1 = column.x1
                return redacted_rect

        raise ValueError("Unable to find rect in column")

    def maybe_add_line_break(self, redacted_rect: pymupdf.Rect):
        """
        This function checks if we can find any text below our redacted rect. If so, we will calculate
        the empty space between them before extending the redacted rect to cover this whitespace. This
        will allow us to account for it later when we are repositioning the text below it.
        If we do not find any text below our redacted rect, we return the redacted rect as is

        TODO handle when
        """

        # use a negative offset to generate a rect of the same size underneath our redacted rect
        offset_by_redacted_rect = -1 * (redacted_rect.height + 1)
        redacted_block = list(redacted_rect)
        rect_underneath_redacted_rect = self._get_rect(redacted_block, offset_by_redacted_rect)

        # search new rect for any text, rebuilding text rect to only encapsulate that text if found
        text_underneath_redacted_rect = self.unified_template_page.get_textbox(rect_underneath_redacted_rect)
        rects_containing_text_underneath = self.unified_template_page.search_for(text_underneath_redacted_rect)

        text_rect = self._combine_rects(rects_containing_text_underneath)

        if text_rect and not text_rect.intersects(redacted_rect):
            # shrink our redacted rect to just above our text_rect
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
        redacted rects to determine how much we are moving the repositioned text up by.
        """
        pass

    def split_unified_pdf(self, unified_pdf):
        """
        Splits our unified PDF into the number of pages found on our original template PDF
        """

        return self.template_resume.file

    def out_of_bounds(self, rect):
        return not self.unified_template_page.rect.contains(rect)

    def _generate_unified_pdf(self):
        page_count, page_width, page_height = self.template_pdf_details.values()
        new_pdf = pymupdf.open()
        new_pdf.new_page(width=page_width, height=page_height * page_count)
        return new_pdf

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
