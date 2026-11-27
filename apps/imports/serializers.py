from rest_framework import serializers


class ExcelImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError(
                'Only .xlsx files are supported.'
            )

        return value