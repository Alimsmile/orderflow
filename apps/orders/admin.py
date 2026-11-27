from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "price", "subtotal_display")
    readonly_fields = ("subtotal_display",)

    @admin.display(description="Стоимость позиции")
    def subtotal_display(self, obj):
        if obj.pk and obj.price is not None and obj.quantity is not None:
            return obj.subtotal
        return "—"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_date", "customer", "total_amount")
    list_filter = ("customer",)
    search_fields = ("customer__name",)
    list_select_related = ("customer",)
    inlines = (OrderItemInline,)
