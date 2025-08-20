import pymupdf
import pytest

from tailor.domain.tailor_resume import TailorPdf
from tailor.models import Resume

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
def tailor_pdf(db, request, bullets_to_redact):
    filename = request.param
    template_resume = Resume.objects.get(id=4)
    return TailorPdf(template_resume, bullets_to_redact)


def fetch_text(resume: Resume):
    filepath = resume.file.path
    pdf = pymupdf.open(filepath)
    text = ""
    for page in pdf:
        text += page.get_text()

    return text

class TestTailorPdf:
    class TestGenerateUnifiedPdf:

        # @pytest.mark.parametrize("template_resume", [
        #     "Arvind Chandra - Resume - 2025.pdf",
        # ], indirect=True)
        # def test_generates_unified_pdf_with_correct_dimensions(self, tailor_pdf: TailorPdf):
        #     template_resume = tailor_pdf.template_resume.file
        #     unified_resume = tailor_pdf.generate_unified_pdf()
        #     assert tailor_pdf.template_pdf_details


        @pytest.mark.parametrize("tailor_pdf", [
            "Arvind Chandra - Resume - 2025.pdf",
        ], indirect=True)
        def test_generates_unified_pdf_with_correct_text(self, tailor_pdf: TailorPdf):
            template_resume = tailor_pdf.template_resume.file
            unified_resume = tailor_pdf.generate_unified_pdf()
            assert fetch_text(template_resume) == fetch_text(unified_resume)


    class TestCalculateSpacing:
        pass

    class TestRedactBullets:
        pass

    class TestFormatPdf:
        pass

    class TestSplitPdf:
        pass

    def default(self):
        pass




