from rest_framework import serializers
from core.models import CodeSpace, TmpCodeSpace
from codespace.tokens import codespace_access_token_generator
from collections import OrderedDict
from typing import Type, Union
import uuid


class CodeSpaceSerializer(serializers.ModelSerializer):
    """Serialize CodeSpace Model"""

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = CodeSpace
        fields = (
            "uuid",
            "name",
            "code",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uuid",
            "code",  # code should be updated only through websockets
            "created_by",
            "created_at",
            "updated_at",
        )

    def get_created_by(self, obj: Type[CodeSpace]) -> Union[str, None]:
        """Return first and last name of codespace creator instead of uuid"""

        if (creator := obj.created_by) and creator.first_name and creator.last_name:
            return f"{creator.first_name} {creator.last_name}".strip()
        else:
            return None

    def get_fields(self) -> Type[OrderedDict]:
        """
        Returns a dictionary of {field_name: field_instance}.
        Allows user to specify "fields" query parameter to return
        only subset of fields
        """

        declared_fields = super().get_fields()

        if fields := self.context["request"].query_params.get("fields"):
            field_names = fields.split(",")
            # Determine the fields that should be included on the serializer.
            fields = OrderedDict()
            for field_name in field_names:
                if field_name in declared_fields:
                    fields[field_name] = declared_fields[field_name]
                else:
                    raise serializers.ValidationError(f"Unknown field - {field_name}")

            return fields
        else:
            return declared_fields


class CodeSpaceTokenSerializer(CodeSpaceSerializer):
    """
    Serializer used in retrieve CodeSpace data with token.
    Overwrite CodeSpaceSerializer by adding mode field
    """

    mode = serializers.SerializerMethodField(allow_null=False)

    class Meta(CodeSpaceSerializer.Meta):
        fields = (
            "uuid",
            "name",
            "code",
            "created_by",
            "created_at",
            "updated_at",
            "mode",
        )
        read_only_fields = (
            "uuid",
            "code",  # code should be updated only through websockets
            "created_by",
            "created_at",
            "updated_at",
            "mode",
        )

    def get_mode(self, obj):
        """
        Get access token mode
        """

        return self.context["view"].kwargs.get("mode")


class TmpCodeSpaceSerializer(serializers.Serializer):
    """
    Temporary codespace is used to store only code without
    any additional data, because it will be automatically deleted
    from redis after time without updates defined in settings
    """

    uuid = serializers.UUIDField(default=lambda: f"tmp-{uuid.uuid4()}")
    code = serializers.CharField(required=False)

    def create(self, validated_data: list) -> dict:
        # used to create new temporary
        # codespace
        tmp_codespace = TmpCodeSpace(**validated_data)
        tmp_codespace.save()
        return tmp_codespace

    def validate(self, attrs: dict) -> dict:
        """used to add 'tmp-' prefix for uuid field"""
        data = super().validate(attrs)

        if not str(data.get("uuid", "")).startswith("tmp-"):
            data.update({"uuid": f"tmp-{data.get('uuid')}"})

        return data


class TokenAccessCodeSpaceSerializer(serializers.Serializer):
    """
    Serializer for codespace access token
    """

    token_generator = codespace_access_token_generator
    # fields
    codespace_uuid = serializers.UUIDField(required=True)
    expire_time = serializers.IntegerField(required=True)
    mode = serializers.ChoiceField(required=True, choices=["edit", "view_only"])

    @classmethod
    def get_token(cls, codespace_uuid: str, expire_time: int, mode: str) -> str:
        """
        Return token created with CodeSpaceAccessToken class
        """

        return cls.token_generator.make_token(codespace_uuid, expire_time, mode)

    def validate(self, attrs: dict) -> dict:
        """
        Validate given data and if it is valid, add generated token
        """

        data = super().validate(attrs)
        token = self.get_token(
            data.get("codespace_uuid"), data.get("expire_time"), data.get("mode")
        )
        data = {"token": token}

        return data
