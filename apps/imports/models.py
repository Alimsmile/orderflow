from django.db import models


class ImportBatch(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает обработки"
        PROCESSING = "processing", "Обрабатывается"
        COMPLETED = "completed", "Завершён"
        FAILED = "failed", "Ошибка"

    file_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    total_rows = models.PositiveIntegerField(default=0)
    imported_rows = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'импорт'
        verbose_name_plural = 'импорты'

    def __str__(self):
        return self.file_name
