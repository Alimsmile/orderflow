from django.contrib import admin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "total_rows", "imported_rows", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("file_name",)

    readonly_fields = (
        "total_rows",
        "imported_rows",
        "error_message",
        "created_at",
        "completed_at",
    )
