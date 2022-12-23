from rest_framework import serializers
from core.models import CodeSpace, TmpCodeSpace
import uuid


class CodeSpaceSerializer(serializers.ModelSerializer):
    """Serialize CodeSpace Model"""

    class Meta:
        model = CodeSpace
        fields = (
            "uuid",
            "name",
            "code",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uuid",
            "created_at",
            "updated_at",
        )


class TmpCodeSpaceSerializer(serializers.Serializer):
    """
    Temporary codespace is used to store only code without
    any additional data, because it will be automatically deleted
    from redis after time without updates defined in settings
    """

    uuid = serializers.UUIDField(default=lambda: f"tmp-{uuid.uuid4()}")
    code = serializers.CharField(required=False)

    def create(self, validated_data) -> dict:
        # used to create new temporary
        # codespace
        tmp_codespace = TmpCodeSpace(**validated_data)
        tmp_codespace.save()
        return tmp_codespace
