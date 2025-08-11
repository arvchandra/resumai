import json
from io import BytesIO
from django.contrib.auth.models import User
from django.db import models
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound, ValidationError

from .domain.tailor_resume import TailorPdf
from .mixins import TimestampMixin

from .domain.openai_api import fetch_openai_response


class Resume(TimestampMixin, models.Model):
    name = models.CharField()
    description = models.CharField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    file = models.FileField(upload_to="resumes/")
    file_name = models.CharField()
    file_type = models.CharField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If this is the first resume uploaded for a user, set it as the default resume
        if not Resume.objects.filter(user=self.user).exists():
            self.is_default = True
        # Set an existing resume as the default resume
        elif (self.pk and self.is_default):
            if self.pk:
                Resume.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)

        super().save(*args, **kwargs)


class TailoredResumeManager(models.Manager):
    def create_from_params(self, user_id: int, resume_id: int, job_posting_url: str):
        user = User.objects.get(pk=user_id)
        template_resume = self._fetch_resume(resume_id, user.id)

        openai_response = fetch_openai_response(template_resume, job_posting_url)
        print(openai_response)
        # return NotFound
        #
        company = openai_response.job_posting_company
        role = openai_response.job_posting_role
        bullets_to_redact = openai_response.non_relevant_bullet_points

        # company = "test_company"
        # role = "test_role"
        # bullets_to_redact = [
        #     'Completed advanced coursework on Udemy.com to strengthen skills in Django, Python, and React.',
        # ]

        name = f"{user.first_name}_{user.last_name}_{company}_{role}_Resume.pdf"

        tailored_resume_in_bytes = TailorPdf(template_resume, bullets_to_redact).tailored_resume_in_bytes
        print("made it out")
        # raise NotFound("dont create file")
        print()
        tailored_resume = ContentFile(tailored_resume_in_bytes, name=name)
        print("made it past content file")

        model_fields = {
            "name": name,
            "company": company,
            "role": role,
            # TODO need to return the formatted JobPosting url instead
            "job_posting_url": job_posting_url,
            "file": tailored_resume,
            "template_resume": template_resume,
            "user": user
        }

        # check that all fields are defined
        if any(value is None for value in model_fields.values()):
            raise ValidationError("Unable to generate Tailored Resume due to empty field")

        tailored_resume = TailoredResume(**model_fields)
        tailored_resume.save()

        return tailored_resume

    def _fetch_resume(self, resume_id, user_id):
        try:
            template_resume = Resume.objects.get(id=resume_id, user_id=user_id)
            return template_resume
        except (Resume.DoesNotExist, Resume.MultipleObjectsReturned):
            raise NotFound("Error retrieving resume")


class TailoredResume(TimestampMixin, models.Model):
    name = models.CharField()
    company = models.CharField()
    role = models.CharField()
    job_posting_url = models.URLField()
    file = models.FileField(upload_to="tailored_resumes/")

    template_resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = TailoredResumeManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("name", "job_posting_url", "user"),
                name="unique_resume_name_per_posting_per_user"
            )
        ]
