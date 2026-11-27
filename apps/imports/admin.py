from django.contrib import admin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "status", "total_rows", "imported_rows", "created_at", "updated_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("file_name",)

    def has_change_permission(self, request, obj=None):
        return False
