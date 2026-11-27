from datetime import datetime
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import DecimalField, F, Sum
from django.db.models.functions import Coalesce


from apps.customers.models import Customer
from apps.catalog.models import Category, Product
from apps.orders.models import Order, OrderItem
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

    @staticmethod
    @transaction.atomic
    def import_orders(batch: ImportBatch, rows: list) -> None:
        orders = {}

        for row_number, row in rows:
            customer, _ = Customer.objects.update_or_create(
                external_id=str(row["customer_id"]).strip(),
                defaults={
                    "name": str(row["customer_name"]).strip(),
                },
            )

            category, _ = Category.objects.update_or_create(
                external_id=str(row["category_id"]).strip(),
                defaults={
                    "name": str(row["category_name"]).strip(),
                },
            )

            product, _ = Product.objects.update_or_create(
                sku=str(row["product_sku"]).strip(),
                defaults={
                    "name": str(row["product_name"]).strip(),
                    "price": Decimal(str(row["price"])),
                    "category": category,
                },
            )

            order_date = row["order_date"]

            if isinstance(order_date, datetime):
                order_date = order_date.date()

            order, _ = Order.objects.update_or_create(
                external_id=str(row["order_id"]).strip(),
                defaults={
                    "customer": customer,
                    "order_date": order_date,
                },
            )

            OrderItem.objects.update_or_create(
                order=order,
                product=product,
                defaults={
                    "quantity": int(row["quantity"]),
                    "price": Decimal(str(row["price"])),
                },
            )

            orders[order.pk] = order

        # Пересчитываем сумму каждого затронутого заказа.
        for order in orders.values():
            total = OrderItem.objects.filter(
                order=order,
            ).aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price"),
                        output_field=DecimalField(
                            max_digits=14,
                            decimal_places=2,
                        ),
                    ),
                    Decimal("0.00"),
                )
            )["total"]

            order.total_amount = total
            order.save(update_fields=["total_amount"])

        batch.total_rows = len(rows)
        batch.imported_rows = len(rows)

        batch.save(update_fields=[
            "total_rows",
            "imported_rows",
            "updated_at",
        ])