from resumai.backend.tailor.models import TailoredResume


class TailorResume:
    def __init__(self):
        tailored_resume = TailoredResume()
        tailored_resume.name = uploaded_file.name
        new_resume_upload.file = uploaded_file
        new_resume_upload.file_type = file_type
        new_resume_upload.user = User.objects.get(id=user_id)  # TODO: Get user from auth
        new_resume_upload.save()