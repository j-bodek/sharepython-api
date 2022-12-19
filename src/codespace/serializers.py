from rest_framework import serializers
from core.models import CodeSpace


class CodeSpaceSerializer(serializers.ModelSerializer):
    """Serialize CodeSpace Model"""

    class Meta:
        model = CodeSpace
        fields = (
            "uuid",
            "name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uuid",
            "created_at",
            "updated_at",
        )
