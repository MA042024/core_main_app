"""Serializers used throughout the Rest API
"""
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from core_main_app.components.template.models import Template


class TemplateSerializer(ModelSerializer):
    """
    Template serializer
    """

    content = CharField(required=True)
    dependencies_dict = CharField(write_only=True, required=False)

    class Meta(object):
        model = Template
        fields = [
            "id",
            "user",
            "filename",
            "content",
            "hash",
            "dependencies",
            "dependencies_dict",
        ]

        read_only_fields = [
            "id",
            "user",
            "hash",
            "_display_name",
        ]
