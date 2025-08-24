import pymupdf
import pytest

from tailor.domain.tailor_resume import TailorPdf


@pytest.fixture
def bullets_to_redact():
    return [
        'Designed and developed a full-stack Django/React application integrating AI-driven prompts and third-party APIs.',
        'Pursued freelance projects in music production and video editing, expanding creative and technical versatility.',
        'Developed the Django/Python/React/Typescript/Postgres Learning Management Platform and the Django Admin.',
        'Led a technical debt resolution strategy in collaboration with the CTO, which resulted in consistent allotment of time and resources to fixing bugs and improving user experience.',
        'Deployed the Docker application to AWS through a customized GitHub Actions pipeline, which included linting, unit and integration testing, and feature-flag testing on both Staging and Production servers.',
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
    ]

@pytest.fixture
def tailor_pdf(resume_object, bullets_to_redact):
    return TailorPdf(resume_object, bullets_to_redact)


expected_columns = {
    "test_arvind_resume.pdf": 1,
    "test_max_resume.pdf": 2
}


class TestTailorPdf:
    class TestGenerateUnifiedPdf:

        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_generates_unified_pdf_with_correct_text(self, resume_object, bullets_to_redact):
            template_resume_doc = pymupdf.open(resume_object.file.path)
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            unified_resume_doc = tailor_pdf.generate_unified_pdf()
            assert fetch_text(template_resume_doc) == fetch_text(unified_resume_doc)

        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_generates_unified_pdf_with_correct_dimensions(self, resume_object, bullets_to_redact):
            template_resume_doc = pymupdf.open(resume_object.file.path)
            template_resume_details = {
                "pages": template_resume_doc.page_count,
                "page_width": template_resume_doc[0].rect.width,
                "page_height": template_resume_doc[0].rect.height
            }
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            unified_resume_doc = tailor_pdf.generate_unified_pdf()
            unified_resume_rect = unified_resume_doc[0].bound()
            assert unified_resume_rect.width == template_resume_details["page_width"]
            assert unified_resume_rect.height == template_resume_details["pages"] * template_resume_details["page_height"]

        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_when_template_resume_is_none(self, resume_object, bullets_to_redact):
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            tailor_pdf.template_resume = None
            with pytest.raises(FileNotFoundError):
                tailor_pdf.generate_unified_pdf()

        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_when_template_resume_has_no_file(self, resume_object, bullets_to_redact):
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            resume_object.file = None
            tailor_pdf.template_resume = resume_object
            with pytest.raises(FileNotFoundError):
                tailor_pdf.generate_unified_pdf()

    class TestCalculateSpacing:
        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_calculates_the_correct_number_of_columns(self, resume_object, bullets_to_redact):
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            unified_resume_doc = tailor_pdf.generate_unified_pdf()
            tailor_pdf.calculate_spacing(unified_resume_doc)
            assert len(tailor_pdf.column_rects) == expected_columns.get(resume_object.filename(), None)

        @pytest.mark.parametrize("resume_object", [
            "test_arvind_resume.pdf",
            "test_max_resume.pdf"
        ], indirect=True)
        def test_calculate_the_correct_number_of_page_breaks(self, resume_object, bullets_to_redact):
            tailor_pdf = TailorPdf(resume_object, bullets_to_redact)
            unified_resume_doc = tailor_pdf.generate_unified_pdf()
            tailor_pdf.calculate_spacing(unified_resume_doc)
            template_page_count = tailor_pdf.template_pdf_details["page_count"]
            assert len(tailor_pdf.page_break_rects) == template_page_count - 1


    class TestRedactBullets:
        pass

    class TestFormatPdf:
        pass

    class TestSplitPdf:
        pass

    class TestGetRect:
        def test_successfully_creates_rect(self, tailor_pdf):
            expected_rect = pymupdf.Rect([0, 0, 100, 100])
            rect = tailor_pdf._get_rect([0, 0, 100, 100])
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
            with pytest.raises(ValueError) as empty_error:
                tailor_pdf._combine_rects(empty_rect_list)
            assert str(empty_error.value) == "No items passed in to combine"

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
