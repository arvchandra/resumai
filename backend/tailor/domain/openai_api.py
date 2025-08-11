from rest_framework.exceptions import ValidationError
from openai import OpenAI
from pydantic import BaseModel
from django.conf import settings

from .document import DocumentFactory
from .job_posting import LinkedInPosting
from tailor.exceptions import ParsingError


class ParsedResumeAndJobDetails(BaseModel):
    most_relevant_resume_bullets: list[str]
    non_relevant_bullet_points: list[str]
    job_posting_company: str
    job_posting_role: str


def fetch_openai_response(resume, job_posting_url: str):
    resume_text = fetch_resume_text(resume)
    job_posting_text = fetch_job_posting_text(job_posting_url)

    print(resume_text)
    # raise ParsingError("exit early")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = {
        "id": "pmpt_686808032cc88193914ee3c0726c26fc06b6bcce04c3ec55",
        "version": "14",
        "variables": {
            "job_posting": job_posting_text,
            "resume": resume_text
        }
    }

    # response = client.responses.create(prompt=prompt)

    response = client.responses.parse(
        prompt=prompt,
        text_format=ParsedResumeAndJobDetails
    )

    if not response.output_parsed:
        raise ParsingError("Unable to fetch response text from OpenAI")

    return response.output_parsed


def fetch_resume_text(resume):
    resume_document = DocumentFactory.create(resume.file)
    resume_text = resume_document.get_text()

    return resume_text


def fetch_job_posting_text(job_posting_url: str):
    # TODO create JobPostingFactory
    if "linkedin.com" not in job_posting_url:
        raise ValidationError("Invalid job posting URL. Must be from www.linkedin.com")

    linkedin_job_posting = LinkedInPosting(job_posting_url)
    job_posting_text = linkedin_job_posting.get_text()

    return job_posting_text
