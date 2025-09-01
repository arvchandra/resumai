import pymupdf
import pytest

from tailor.domain.tailor_resume import TailorPdf
from test_constants import *


@pytest.fixture
def tailor_pdf(request, resume_object):
    build_level = request.param if hasattr(request, "param") else None
    bullets_to_redact = BULLETS_TO_REDACT.get(resume_object.filename())

    tailor_pdf = TailorPdf(resume_object, bullets_to_redact)

    if not build_level:
        return tailor_pdf

    tailor_pdf.generate_unified_pdf()
    tailor_pdf.calculate_spacing()

    if build_level == "CALCULATE_SPACING":
        return tailor_pdf

    tailor_pdf.redact_bullets_from_pdf()

    if build_level == "REDACT_BULLETS":
        return tailor_pdf

    return TailorPdf(resume_object, bullets_to_redact)


class TestTailorPdf:
    class TestGenerateUnifiedPdf:

        def test_generates_unified_pdf_with_correct_text(self, tailor_pdf):
            template_resume_doc = pymupdf.open(tailor_pdf.template_resume.file.path)
            tailor_pdf.generate_unified_pdf()
            assert fetch_text(template_resume_doc) == fetch_text(tailor_pdf.unified_template_page.parent)

        def test_generates_unified_pdf_with_correct_dimensions(self, tailor_pdf):
            template_resume_doc = pymupdf.open(tailor_pdf.template_resume.file.path)
            template_resume_details = {
                "pages": template_resume_doc.page_count,
                "page_width": template_resume_doc[0].rect.width,
                "page_height": template_resume_doc[0].rect.height
            }
            tailor_pdf.generate_unified_pdf()
            template_page = tailor_pdf.unified_template_page
            unified_resume_rect = template_page.bound()
            assert unified_resume_rect.width == template_resume_details["page_width"]
            assert unified_resume_rect.height == template_resume_details["pages"] * template_resume_details["page_height"]

        def test_when_template_resume_is_none(self, tailor_pdf):
            tailor_pdf.template_resume = None
            with pytest.raises(FileNotFoundError):
                tailor_pdf.generate_unified_pdf()

        def test_when_template_resume_has_no_file(self, tailor_pdf):
            tailor_pdf.template_resume.file = None
            with pytest.raises(FileNotFoundError):
                tailor_pdf.generate_unified_pdf()

    class TestCalculateSpacing:
        @pytest.mark.parametrize("tailor_pdf", ["CALCULATE_SPACING"], indirect=True)
        def test_calculates_the_correct_number_of_columns(self, tailor_pdf):
            assert len(tailor_pdf.column_rects) == EXPECTED_COLUMNS.get(tailor_pdf.template_resume.filename(), None)

        @pytest.mark.parametrize("tailor_pdf", ["CALCULATE_SPACING"], indirect=True)
        def test_calculate_the_correct_number_of_page_breaks(self, tailor_pdf):
            template_page_count = tailor_pdf.template_pdf_details["page_count"]
            assert len(tailor_pdf.page_break_rects) == template_page_count - 1

    class TestRedactBullets:
        @pytest.mark.parametrize("tailor_pdf", ["CALCULATE_SPACING"], indirect=True)
        def test_successfully_redacts_bullets(self, tailor_pdf):
            template_page = tailor_pdf.unified_template_page
            initial_bullets = [bullet for bullet in tailor_pdf.bullets_to_redact if template_page.search_for(bullet)]
            assert initial_bullets
            tailor_pdf.redact_bullets_from_pdf()
            remaining_bullets = [bullet for bullet in tailor_pdf.bullets_to_redact if template_page.search_for(bullet)]
            assert not remaining_bullets

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_redacted_borders_are_formatted_correctly(self, tailor_pdf):
            redacted_rect_borders = [(rect.x0, rect.x1) for rect in tailor_pdf.redacted_rects]
            expected_borders = [(column.x0, column.x1) for column in tailor_pdf.column_rects]
            assert all([rect_boarders in expected_borders for rect_boarders in redacted_rect_borders])

        def test_raises_error_when_nothing_is_redacted(self, tailor_pdf):
            tailor_pdf.bullets_to_redact = []
            tailor_pdf.generate_unified_pdf()
            tailor_pdf.calculate_spacing()
            with pytest.raises(ValueError) as empty_bullet_error:
                tailor_pdf.redact_bullets_from_pdf()
            assert str(empty_bullet_error.value) == "No redactions applied"

    class TestFormatPdf:
        pass

    class TestTextRectOffset:
        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_bullet_above_rect_not_changed(self, tailor_pdf):
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, 0
            expected_redacted_rect_offset = expected_redacted_rect_index = 0

            bullet_above_redacted_text = BULLETS_ABOVE_FIRST_REDACTED.get(tailor_pdf.template_resume.filename())
            above_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_above_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index, above_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_bullet_below_redacted_offsets_correctly(self, tailor_pdf):
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page,  0
            first_redacted_rect = tailor_pdf.redacted_rects[redacted_rect_index]
            expected_redacted_rect_offset, expected_redacted_rect_index = first_redacted_rect.height, 1

            bullet_below_redacted_text = BULLETS_BELOW_FIRST_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_below_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_bullet_below_consecutive_redacted_offsets_correctly(self, tailor_pdf):
            redacted_page = tailor_pdf.unified_template_page
            redacted_rect_index = CONSECUTIVE_REDACTED_INDEX.get(tailor_pdf.template_resume.filename())
            first_consecutive_redacted_rect = tailor_pdf.redacted_rects[redacted_rect_index]
            second_consecutive_redacted_rect = tailor_pdf.redacted_rects[redacted_rect_index+1]
            combined_distance = second_consecutive_redacted_rect.y1 - first_consecutive_redacted_rect.y0
            expected_redacted_rect_offset, expected_redacted_rect_index = combined_distance, redacted_rect_index+2
            # There is no line break spacing between our redacted_rect bullets
            assert first_consecutive_redacted_rect.height + second_consecutive_redacted_rect.height == combined_distance

            text_below_redacted_text = TEXT_BELOW_CONSECUTIVE_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(text_below_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_when_we_reach_the_end_of_our_redacted_list_while_offsetting(self, tailor_pdf):
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, len(tailor_pdf.redacted_rects) - 1
            last_redacted_rect = tailor_pdf.redacted_rects[redacted_rect_index]
            expected_redacted_rect_offset, expected_redacted_rect_index = last_redacted_rect.height, redacted_rect_index + 1

            bullet_below_last_redacted_text = TEXT_BELOW_LAST_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_below_last_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_no_redacted_rects(self, tailor_pdf):
            tailor_pdf.redacted_rects = []
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, 0
            expected_redacted_rect_offset = expected_redacted_rect_index = 0

            bullet_below_first_redacted_text = BULLETS_BELOW_FIRST_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_below_first_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_reached_end_of_redacted_rects(self, tailor_pdf):
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, len(tailor_pdf.redacted_rects)
            expected_redacted_rect_offset, expected_redacted_rect_index = 0, redacted_rect_index

            bullet_above_first_redacted_text = BULLETS_BELOW_FIRST_REDACTED.get(tailor_pdf.template_resume.filename())
            above_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_above_first_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    above_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_isolates_only_text_block(self, tailor_pdf):
            redacted_page = tailor_pdf.unified_template_page
            first_text_block = redacted_page.get_text("blocks")[0]
            first_text_rect = tailor_pdf._get_rect(first_text_block)
            repositioned_text_block = tailor_pdf._get_rect(first_text_block, offset=-10)
            isolated_pdf = tailor_pdf.isolate_repositioned_rect(repositioned_text_block, redacted_page.parent, first_text_rect)

            isolated_pdf_text = isolated_pdf[0].get_text("blocks")
            assert len(isolated_pdf_text) == 1
            isolated_pdf_rect = tailor_pdf._get_rect(isolated_pdf_text[0])
            assert isolated_pdf_rect == repositioned_text_block
            assert isolated_pdf[0].get_textbox(isolated_pdf_rect) == redacted_page.get_textbox(first_text_rect)

    class TestSplitPdf:
        pass

    class TestGetRect:
        def test_successfully_creates_rect_from_sequence(self, tailor_pdf):
            expected_rect = pymupdf.Rect([0, 0, 100, 100])
            rect = tailor_pdf._get_rect([0, 0, 100, 100])
            assert rect == expected_rect

        def test_successfully_creates_rect_from_rect(self, tailor_pdf):
            expected_rect = pymupdf.Rect([0, 0, 100, 100])
            rect = tailor_pdf._get_rect(expected_rect)
            assert rect == expected_rect

        @pytest.mark.parametrize("offset", [0, 50, -50])
        def test_successfully_creates_rect_with_offset(self, tailor_pdf, offset):
            expected_rect = pymupdf.Rect([100, 100 - offset, 200, 200 - offset])
            rect = tailor_pdf._get_rect([100, 100, 200, 200], offset)
            assert rect == expected_rect

        @pytest.mark.parametrize("impossible_rect_value", [
            (0, 0, 0, 0),
            (0, 100, 0, 150),
            (100, 100, 0, 0),
        ])
        def test_invalid_or_empty_rect(self, tailor_pdf, impossible_rect_value):
            with pytest.raises(ValueError) as impossible_rect_error:
                tailor_pdf._get_rect(impossible_rect_value)
            assert str(impossible_rect_error.value) == "Rect is empty or invalid"

        @pytest.mark.parametrize("rect_parameters", [
            (0, 100),
            ("0", "0", "100", "100"),
        ])
        def test_invalid_parameters(self, tailor_pdf, rect_parameters):
            with pytest.raises(ValueError) as pymupdf_error:
                tailor_pdf._get_rect(rect_parameters)
            assert str(pymupdf_error.value) == "Invalid parameters when generating Rect"

    class TestCombineRect:
        @pytest.mark.parametrize("rect_list", [
            [pymupdf.Rect(0, 0, 100, 100), pymupdf.Rect(100, 100, 200, 200)],
            [pymupdf.Rect(0, 0, 100, 100), pymupdf.Rect(50, 0, 75, 90)],
            [pymupdf.Rect(50, 0, 75, 90), pymupdf.Rect(0, 0, 100, 100)],
            [(0, 0, 100, 100), (100, 100, 200, 200)],
            [(0, 0, 100, 100), (50, 0, 75, 90)],
            [(50, 0, 75, 90), (0, 0, 100, 100)],
        ])
        def test_successfully_combines_rect(self, tailor_pdf, rect_list):
            max_x0 = min([rect[0] for rect in rect_list])
            max_y0 = min([rect[1] for rect in rect_list])
            max_x1 = max([rect[2] for rect in rect_list])
            max_y1 = max([rect[3] for rect in rect_list])
            expected_rect = pymupdf.Rect(max_x0, max_y0, max_x1, max_y1)

            combined_rect = tailor_pdf._combine_rects(rect_list)
            assert combined_rect == expected_rect

        def test_when_empty_list(self, tailor_pdf):
            empty_rect_list = []
            returned_rect = tailor_pdf._combine_rects(empty_rect_list)
            assert returned_rect is None

        @pytest.mark.parametrize("impossible_rect_values", [
            (0, 0, 0, 0),
            (0, 100, 0, 150),
            (100, 100, 0, 0),
        ])
        def test_when_impossible_rect(self, tailor_pdf, impossible_rect_values):
            impossible_rect = pymupdf.Rect(impossible_rect_values)
            with pytest.raises(ValueError) as impossible_error:
                tailor_pdf._combine_rects([impossible_rect])
            assert str(impossible_error.value) == "Unable to generate a valid combined rect"


def fetch_text(resume_doc: pymupdf.Document):
    text = ""
    for page in resume_doc:
        text += page.get_text()
    return text
