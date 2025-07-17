from rest_framework import serializers

from tailor.models import Resume, TailoredResume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'name', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class TailoredResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailoredResume
        fields = ['name', 'company', 'role', 'job_posting', 'file']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
