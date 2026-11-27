from django.utils import timezone

from celery import shared_task

from .models import ImportBatch


@shared_task
def process_import_batch(batch_id):
    batch = ImportBatch.objects.get(id=batch_id)

    batch.status = ImportBatch.Status.PROCESSING
    batch.save(update_fields=['status', 'updated_at'])

    try:
        # TODO: чтение Excel
        # TODO: валидация строк
        # TODO: импорт данных

        batch.status = ImportBatch.Status.COMPLETED
        batch.completed_at = timezone.now()
        batch.save(update_fields=['status', 'completed_at', 'updated_at'])

    except Exception as exc:
        batch.status = ImportBatch.Status.FAILED
        batch.error_message = str(exc)
        batch.save(
            update_fields=['status', 'error_message', 'updated_at']
        )
        raise