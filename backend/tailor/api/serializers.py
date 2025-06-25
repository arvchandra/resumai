from rest_framework import serializers
from tailor.models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'user', 'file', 'name', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
