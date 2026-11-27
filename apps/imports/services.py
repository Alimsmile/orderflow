from django.db import transaction

from .models import ImportBatch
from .tasks import process_import_batch


class ImportService:

    @staticmethod
    def create_import(file):
        with transaction.atomic():
            batch = ImportBatch.objects.create(
                file=file,
                file_name=file.name,
            )

            transaction.on_commit(
                lambda: process_import_batch.delay(str(batch.id))
            )

        return batch