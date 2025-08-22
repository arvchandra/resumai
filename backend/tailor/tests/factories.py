import factory
from django.contrib.auth.models import User
from tailor.models import Resume


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')


class ResumeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resume

    name = "Demo_Resume"
    file = "resumes/test_arvind_resume.pdf"
    file_type = "PDF"
    user = factory.SubFactory(UserFactory)
