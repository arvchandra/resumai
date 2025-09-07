
import pymupdf
import pytest

from tailor.domain.tailor_resume import TailorPdf

EXPECTED_COLUMNS = {
    "test_arvind_resume.pdf": 1,
    "test_max_resume.pdf": 2
}

BULLETS_TO_REDACT = {
    "test_arvind_resume.pdf": [
        'Pursued freelance projects in music production and video editing, expanding creative and technical versatility.',
        'Developed the Django/Python/React/Typescript/Postgres Learning Management Platform and the Django Admin.',
        'Led a technical debt resolution strategy in collaboration with the CTO, which resulted in consistent allotment of time and resources to fixing bugs and improving user experience.',
        'Deployed the Docker application to AWS through a customized GitHub Actions pipeline, which included linting, unit and integration testing, and feature-flag testing on both Staging and Production servers.', # TODO Causing problems with next job experience spacing
        'Generated 300% increase in revenue for the Press Release product by converting a basic HTML form into a more robust and user-friendly single-page React application.',
        'Developed React/Typescript components and a Django REST Framework API, which enabled features such as bulk purchases, discount codes, and Stripe payments, incorporating both server-side and client-side validation.',
        'Reduced average debugging time by 50% by enabling breakpoint-debugging of code running inside Docker containers, in both Visual Studio Code and PyCharm.',
        'Developed the Django/Python/MySQL online news websites and the Django Admin using Django/Jinja templates, HTML, CSS, and Javascript/jQuery.',
        'Led the implementation of Agile/Scrum development, including sprints, retroactives, and JIRA tickets/epics.',
        'Generated $10,000 in weekly ad sales revenue by implementing an HTML5/CSS video ad on our landing page.',
        'Developed a Django REST Framework API that delivered cached results to the frontend Used Cars search website.',
        'Achieved 500% improvement in time efficiency (5 days to 2 hours) for our team of writers by creating an automated scraping framework that retrieved car deals from numerous vehicle manufacturer websites.',
        'Interviewed and hired senior Django developers.',
        'Established a robust testing framework by writing over 300 unit tests.',
        'Lowered annual costs by $15,000 by reassessing IBM Cognos Reports usage and reducing license purchases.',
        'Received a letter of commendation from the client for outstanding performance in understanding the business requirements, delivering high-quality and secure application features, and meeting critical government deadlines.',
    ],
    "test_max_resume.pdf": [
        "Refactored legacy Whatsapp API and expanded internal tooling in Ruby to surface errors, reducing support request volume by 15%.",
        "Engineered data ingestion pipeline API across microservices using Python and PostgreSQL for B2C loan product, reducing admin maintenance by 80%.",
        "Ideated event timeline internal tool using asynchronous Python, REST APIs and PostgreSQL to reduce support requests by 25%.",
    ]
}

BULLETS_ABOVE_FIRST_REDACTED = {
    "test_arvind_resume.pdf": "Designed and developed a full-stack Django/React application integrating AI-driven prompts and third-party APIs.",
    "test_max_resume.pdf": "Deputy engineer for async AWS FIFO queue migration in Ruby to address timestamp-sensitive concurrency problem for Service-Level-Agreement(SLA) feature used by enterprise customers; leading post-release handover."
}

BULLETS_BELOW_FIRST_REDACTED = {
    "test_arvind_resume.pdf": "Traveled to India to take care of my parents and oversee the construction of our new house.",
    "test_max_resume.pdf": "Led development of RESTful API to fetch real-time message delivery status of Whatsapp outbound marketing campaigns."
}

TEXT_BELOW_CONSECUTIVE_REDACTED = {
    "test_arvind_resume.pdf": "The Motley Fool",
    "test_max_resume.pdf": "CENTER FOR LONG-TERM CYBERSECURITY | Graduate Researcher"
}

CONSECUTIVE_REDACTED_INDEX = {
    "test_arvind_resume.pdf": 5,
    "test_max_resume.pdf": 1
}

TEXT_BELOW_LAST_REDACTED = {
    "test_arvind_resume.pdf": "University of Michigan - Ann Arbor, MI",
    "test_max_resume.pdf": "TD INTERNATIONAL"
}

TEXT_BELOW_REDACTED_SEPARATE_COLUMN = {
    "test_max_resume.pdf": "Weber, Nagamine, Ingraham-Rakatansky. Presented at GigaNet, Nov. 2020, Katowice, Poland.",
}

REDACTED_TEXT_IN_SEPARATE_COLUMN = {
    "test_max_resume.pdf": "AWS/Python Civic Chatbot"
}


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

    return tailor_pdf


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
            assert len(tailor_pdf.column_data) == EXPECTED_COLUMNS.get(tailor_pdf.template_resume.filename(), None)
            assert all([column["offset"] == 0 for column in tailor_pdf.column_data.values()])

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
            expected_borders = [(column["rect"].x0, column["rect"].x1) for column in tailor_pdf.column_data.values()]
            assert all([rect_boarders in expected_borders for rect_boarders in redacted_rect_borders])

        def test_raises_error_when_nothing_is_redacted(self, tailor_pdf):
            tailor_pdf.bullets_to_redact = []
            tailor_pdf.generate_unified_pdf()
            tailor_pdf.calculate_spacing()
            with pytest.raises(ValueError) as empty_bullet_error:
                tailor_pdf.redact_bullets_from_pdf()
            assert str(empty_bullet_error.value) == "No redactions applied"

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
            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, 0
            first_redacted_rect = tailor_pdf.redacted_rects[redacted_rect_index]
            expected_redacted_rect_offset, expected_redacted_rect_index = first_redacted_rect.height, 1

            bullet_below_redacted_text = BULLETS_BELOW_FIRST_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(bullet_below_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_text_below_redacted_in_separate_column_doesnt_offset(self, tailor_pdf):
            # pass if single column resume
            if len(tailor_pdf.column_data) == 1:
                return True

            redacted_page, redacted_rect_index = tailor_pdf.unified_template_page, 0
            expected_redacted_rect_offset = expected_redacted_rect_index = 0

            text_in_separate_column = TEXT_BELOW_REDACTED_SEPARATE_COLUMN.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(text_in_separate_column))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)
            assert all([column["offset"] == 0 for column in tailor_pdf.column_data.values()])

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_bullet_below_consecutive_redacted_offsets_correctly(self, tailor_pdf):
            redacted_page = tailor_pdf.unified_template_page
            redacted_rect_index = CONSECUTIVE_REDACTED_INDEX.get(tailor_pdf.template_resume.filename())
            combined_distance = tailor_pdf.redacted_rects[redacted_rect_index+1].y1 - tailor_pdf.redacted_rects[redacted_rect_index].y0
            expected_redacted_rect_offset, expected_redacted_rect_index = combined_distance, redacted_rect_index+2

            text_below_redacted_text = TEXT_BELOW_CONSECUTIVE_REDACTED.get(tailor_pdf.template_resume.filename())
            below_rect = tailor_pdf._combine_rects(redacted_page.search_for(text_below_redacted_text))
            redacted_offset, redacted_index = tailor_pdf.calculate_text_rect_offset(redacted_rect_index,
                                                                                    below_rect)
            assert (redacted_offset, redacted_index) == (expected_redacted_rect_offset, expected_redacted_rect_index)

        @pytest.mark.parametrize("tailor_pdf", ["REDACT_BULLETS"], indirect=True)
        def test_text_below_consecutive_redacted_in_separate_columns_offsets_first_only(self, tailor_pdf):
            # pass if single column resume
            if len(tailor_pdf.column_data) == 1:
                return True

            # add extra redacted rect in separate column
            redacted_page = tailor_pdf.unified_template_page
            separate_column_redacted_text = REDACTED_TEXT_IN_SEPARATE_COLUMN.get(tailor_pdf.template_resume.filename())
            separate_column_redacted_blocks = redacted_page.search_for(separate_column_redacted_text)
            separate_redacted_rect = tailor_pdf._combine_rects(separate_column_redacted_blocks)
            tailor_pdf.redacted_rects.append(separate_redacted_rect)

            redacted_rect_index = len(tailor_pdf.redacted_rects) - 2
            first_column_redacted_height = tailor_pdf.redacted_rects[redacted_rect_index].height
            expected_redacted_rect_offset, expected_redacted_rect_index = first_column_redacted_height, redacted_rect_index + 1

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

        @pytest.mark.parametrize("tailor_pdf", ["CALCULATE_SPACING"], indirect=True)
        def test_text_rect_overlaps_with_top_of_page_break(self, tailor_pdf):
            if not tailor_pdf.page_break_rects:
                return True

            first_page_break = tailor_pdf.page_break_rects[0]
            top_of_page_break = first_page_break.y0
            rect_partially_overlapping_page_break = pymupdf.Rect(0, top_of_page_break-10, first_page_break.x1, top_of_page_break+2)
            expected_offset = first_page_break.height + 10
            assert tailor_pdf.maybe_correct_for_page_break(rect_partially_overlapping_page_break) == expected_offset

        @pytest.mark.parametrize("tailor_pdf", ["CALCULATE_SPACING"], indirect=True)
        def test_text_rect_overlaps_with_bottom_of_page_break(self, tailor_pdf):
            if not tailor_pdf.page_break_rects:
                return True

            first_page_break = tailor_pdf.page_break_rects[0]
            bottom_of_page_break = first_page_break.y1
            rect_partially_overlapping_page_break = pymupdf.Rect(0, bottom_of_page_break - 2, first_page_break.x1,
                                                                 bottom_of_page_break + 10)
            expected_offset = 2
            assert tailor_pdf.maybe_correct_for_page_break(rect_partially_overlapping_page_break) == expected_offset

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
        @pytest.mark.parametrize("resume_object", ["test_arvind_resume_extra_page.pdf"], indirect=True)
        def test_splits_unified_pdf_doesnt_include_empty_page(self, resume_object):
            bullets_to_redact = [
                "Arvind Chandra",
                "Senior Software Engineer | Full-Stack Developer | U.S. Citizen",
                "arvchandra@gmail.com | linkedin.com/in/arvchandra | (614) 477-8901",
                "Senior Software Engineer with 8+ years of experience developing robust full-stack web applications using Python/Django and React. Passionate about cross-functional collaboration, translating business requirements into user-friendly features, analyzing data to drive insights, and delivering outstanding customer service through responsive incident resolution. Proven track record of success across fast-paced startups, digital journalism, and government consulting.",
                "Led the rebuild of a complex Customer Survey application – designed the database schema, Django REST API, React/Typescript components, and unit/E2E tests for backend and frontend.",
                "Led CMS development for high-traffic rankings platforms Cars, Travel, and Real Estate using Django and PostgreSQL.",
                "Communicated with editors to identify inefficient processes - led to automating web scraping workflows that reduced data prep time for our editors from 5 days to 2 hours.",
                "WORK AUTHORIZATION",
            ]
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            e = tailor_pdf.create_tailored_resume()
            if e:
                raise e

            tailored_resume = tailor_pdf.tailored_resume
            assert tailored_resume.page_count == tailor_pdf.template_pdf_details["page_count"] - 1

    class TestCreateTailoredResume:
        def test_can_create_tailored_resume(self, tailor_pdf):
            tailor_pdf.create_tailored_resume()
            tailored_resume = tailor_pdf.tailored_resume
            expected_page_count, expected_page_width, expected_page_height = tailor_pdf.template_pdf_details.values()
            expected_page_rect = pymupdf.Rect((0, 0), (expected_page_width, expected_page_height))
            assert tailored_resume.page_count == expected_page_count
            assert all([page.rect == expected_page_rect for page in tailored_resume])

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
