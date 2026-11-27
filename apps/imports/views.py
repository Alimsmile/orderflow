from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .serializers import ExcelImportSerializer
from .services.import_service import ImportService

from apps.imports.exceptions import IdempotencyConflictError


class ExcelImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary='Upload Excel file',
        description='Upload an Excel file for importing orders.',
        request=ExcelImportSerializer,
        responses={201: None},
    )
    def post(self, request):
        idempotency_key = request.headers.get('Idempotency-Key')

        if not idempotency_key:
            return Response(
                {'error': 'Idempotency-Key header is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            batch, created = ImportService.create_import(
                file=serializer.validated_data['file'],
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflictError as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        response_status = (
            status.HTTP_202_ACCEPTED
            if created
            else status.HTTP_200_OK
        )

        return Response(
            {
                'message': 'File uploaded successfully.',
                'batch_id': str(batch.id),
                'status': batch.status,
            },
            response_status,
        )