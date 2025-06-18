from django.contrib.auth.models import User
from django.db import models

from tailor.mixins import TimestampMixin

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