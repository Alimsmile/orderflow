from django.db import IntegrityError, transaction


from apps.imports.models import ImportBatch

from apps.imports.tasks import process_import_batch

from apps.imports.utils import calculate_file_hash

from apps.imports.exceptions import IdempotencyConflictError


class ImportService:

    @staticmethod
    def _get_existing_batch(idempotency_key, file_hash):
        batch = ImportBatch.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if batch is None:
            return None

        if batch.file_hash != file_hash:
            raise IdempotencyConflictError(
                'Idempotency-Key was already used with different file content.'
            )

        return batch

    @staticmethod
    def create_import(file, idempotency_key):
        file_hash = calculate_file_hash(file)

        existing_batch = ImportService._get_existing_batch(
            idempotency_key,
            file_hash,
        )

        if existing_batch:
            return existing_batch, False

        try:
            with transaction.atomic():
                batch = ImportBatch.objects.create(
                    file=file,
                    file_name=file.name,
                    file_hash=file_hash,
                    idempotency_key=idempotency_key,
                )

                transaction.on_commit(
                    lambda: process_import_batch.delay(str(batch.id))
                )

            return batch, True
        except IntegrityError:
            # Другой параллельный запрос мог создать импорт с таким же ключом.
            # Повторно проверяем хеш файла, чтобы отличить повторную загрузку
            # того же файла от попытки использовать ключ с другим содержимым.
            existing_batch = ImportService._get_existing_batch(
                idempotency_key,
                file_hash,
            )

            if existing_batch is None:
                raise

            return existing_batch, False
