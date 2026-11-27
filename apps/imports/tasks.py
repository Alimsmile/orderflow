from django.utils import timezone

from celery import shared_task

from .models import ImportBatch

from .services.excel_parser import parse_excel
from .services.validators import validate_columns, validate_rows


@shared_task
def process_import_batch(batch_id):
    from .services.import_service import ImportService

    batch = ImportBatch.objects.get(id=batch_id)

    batch.status = ImportBatch.Status.PROCESSING
    batch.save(update_fields=['status', 'updated_at'])

    try:
        # Чтение файла
        with batch.file.open("rb") as file:
            headers, rows = parse_excel(file)

        # Валидация
        validate_columns(headers)
        validate_rows(rows)

        batch.total_rows = len(rows)

        # Импорт
        ImportService.import_orders(batch, rows)

        batch.status = ImportBatch.Status.COMPLETED
        batch.completed_at = timezone.now()
        batch.save(update_fields=[
            "status",
            "total_rows",
            "completed_at",
            "updated_at",
        ])

    except Exception as exc:
        batch.status = ImportBatch.Status.FAILED
        batch.error_message = str(exc)
        batch.save(
            update_fields=['status', 'error_message', 'updated_at']
        )
        raise