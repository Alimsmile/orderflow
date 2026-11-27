from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .serializers import ExcelImportSerializer
from .services import ImportService


class ExcelImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary='Upload Excel file',
        description='Upload an Excel file for importing orders.',
        request=ExcelImportSerializer,
        responses={201: None},
    )
    def post(self, request):
        serializer = ExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']

        batch = ImportService.create_import(
            serializer.validated_data['file']
        )

        return Response(
            {
                'message': 'File uploaded successfully.',
                'batch_id': str(batch.id),
                'status': batch.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )