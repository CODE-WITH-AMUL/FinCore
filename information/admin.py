# accountings/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import SupplierModel


@admin.register(SupplierModel)
class SupplierModelAdmin(admin.ModelAdmin):
    # ---------------- List view ----------------
    list_display = (
        'code',
        'name',
        'company_name',
        'supplier_type',
        'supplier_type_company',
        'supplier_status',
        'supplier_rating_badge',
        'city',
        'country',
        'payment_status',
        'created_at',
    )

    list_display_links = ('code', 'name')

    list_filter = (
        'supplier_status',
        'supplier_type',
        'supplier_type_company',
        'supplier_company',
        'payment_status',
        'country',
        'created_at',
    )

    search_fields = (
        'code',
        'name',
        'company_name',
        'email',
        'contact_number',
        'city',
        'provience',
        'country',
        'zip_code',
    )

    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_select_related = False  # no FK here; M2M only
    save_on_top = True

    # ---------------- Read-only fields ----------------
    readonly_fields = ('code', 'created_at', 'updated_at')

    # ---------------- Detail form layout ----------------
    fields = (
    'code', 'name', 'company_name', 'products_supplied',
    'adress', 'city', 'provience', 'country', 'zip_code',
    'History', 'supplier_type', 'supplier_type_company',
    'supplier_status', 'supplier_rating', 'supplier_company',
    'email', 'contact_number', 'payment_status', 'notes',
    'created_at', 'updated_at',
)

    # ---------------- M2M widget ----------------
    filter_horizontal = ('products_supplied',)

    # ---------------- Custom columns ----------------
    @admin.display(description='Rating', ordering='supplier_rating')
    def supplier_rating_badge(self, obj):
        """Colour-coded rating badge for the list view."""
        if obj.supplier_rating is None:
            return '—'
        rating = float(obj.supplier_rating)
        if rating >= 4:
            colour = '#047857'   # green
        elif rating >= 2.5:
            colour = '#b45309'   # amber
        else:
            colour = '#b91c1c'   # red
        return format_html(
            '<span style="display:inline-block;padding:1px 8px;border-radius:10px;'
            'font-weight:600;font-size:11px;color:#fff;background:{};">{}</span>',
            colour,
            f'{rating:.2f}',
        )

    # ---------------- Bulk actions ----------------
    actions = ('mark_active', 'mark_inactive')

    @admin.action(description='Mark selected suppliers as Active')
    def mark_active(self, request, queryset):
        updated = queryset.update(supplier_status='active')
        self.message_user(request, f'{updated} supplier(s) marked as Active.')

    @admin.action(description='Mark selected suppliers as Inactive')
    def mark_inactive(self, request, queryset):
        updated = queryset.update(supplier_status='inactive')
        self.message_user(request, f'{updated} supplier(s) marked as Inactive.')