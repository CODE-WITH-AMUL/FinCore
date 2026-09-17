from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, product_type, Product


# ============================================================
# CATEGORY ADMIN
# ============================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_prefex', 'product_count', 'short_description')
    list_filter = ('code_prefex',)
    search_fields = ('name', 'code_prefex', 'decription')
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code_prefex')
        }),
        ('Description', {
            'fields': ('decription',),
            'classes': ('wide',)
        }),
    )

    @admin.display(description='Products')
    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="font-family:monospace;font-weight:600;">{}</span>',
            count
        )

    @admin.display(description='Description')
    def short_description(self, obj):
        if not obj.decription:
            return "—"
        text = obj.decription[:60]
        if len(obj.decription) > 60:
            text += '…'
        return text


# ============================================================
# PRODUCT TYPE ADMIN
# ============================================================
@admin.register(product_type)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    @admin.display(description='Products')
    def product_count(self, obj):
        count = obj.products_list.count()
        return format_html(
            '<span style="font-family:monospace;font-weight:600;">{}</span>',
            count
        )


# ============================================================
# PRODUCT ADMIN
# ============================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku_display',
        'isp_code_display',
        'category',
        'manufacturer',
        'price_display',
        'stock_status',
        'image_thumbnail',
        'created_at',
    )
    list_filter = (
        'category',
        'types_of_product',
        'manufacturer',
        'created_at',
        'deleted_at',
    )
    search_fields = (
        'name',
        'sku',
        'isp_code',
        'decription',
        'manufacturer',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('category',)

    readonly_fields = (
        'sku',
        'isp_code',
        'created_at',
        'updated_at',
        'image_preview_large',
    )

    fieldsets = (
        ('Identification', {
            'fields': ('name', 'sku', 'isp_code')
        }),
        ('Classification', {
            'fields': ('category', 'types_of_product', 'manufacturer')
        }),
        ('Details', {
            'fields': ('decription', 'price')
        }),
        ('Media', {
            'fields': ('image', 'image_preview_large'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ('types_of_product',)

    # ---------- List display helpers ----------
    @admin.display(description='SKU', ordering='sku')
    def sku_display(self, obj):
        return format_html(
            '<span style="font-family:monospace;background:#f3f4f6;'
            'padding:2px 6px;border-radius:4px;font-size:11px;">{}</span>',
            obj.sku
        )

    @admin.display(description='ISP Code', ordering='isp_code')
    def isp_code_display(self, obj):
        return format_html(
            '<span style="font-family:monospace;background:#f3f4f6;'
            'padding:2px 6px;border-radius:4px;font-size:11px;">{}</span>',
            obj.isp_code
        )

    @admin.display(description='Price', ordering='price')
    def price_display(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-weight:600;">Rs. {}</span>',
            f"{obj.price:,.2f}"
        )

    @admin.display(description='Stock')
    def stock_status(self, obj):
        # Since your model has no stock field, this is a placeholder.
        # Update if you add a `stock_quantity` field.
        return mark_safe(
            '<span style="color:#6b7280;font-size:11px;">—</span>'
        )

    @admin.display(description='Image')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:32px;height:32px;'
                'object-fit:cover;border-radius:4px;border:1px solid #e5e7eb;" />',
                obj.image.url
            )
        return mark_safe(
            '<span style="color:#9ca3af;font-size:11px;">No image</span>'
        )

    @admin.display(description='Preview')
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:280px;max-height:280px;'
                'object-fit:contain;border-radius:6px;border:1px solid #e5e7eb;" />',
                obj.image.url
            )
        return "No image uploaded."

    # ---------- Bulk actions ----------
    actions = ['soft_delete_selected', 'restore_selected']

    @admin.action(description='Soft-delete selected products')
    def soft_delete_selected(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{updated} product(s) soft-deleted.")

    @admin.action(description='Restore selected products')
    def restore_selected(self, request, queryset):
        updated = queryset.update(deleted_at=None)
        self.message_user(request, f"{updated} product(s) restored.")

    # ---------- Queryset optimisation ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category').prefetch_related('types_of_product')

    # ---------- Save behaviour ----------
    def save_model(self, request, obj, form, change):
        # Ensure SKU/ISP are auto-generated only once (on creation)
        if not change:
            obj.sku = obj.sku or obj._meta.get_field('sku').get_default()
            obj.isp_code = obj.isp_code or obj._meta.get_field('isp_code').get_default()
        super().save_model(request, obj, form, change)


# ============================================================
# ADMIN SITE BRANDING (optional)
# ============================================================
admin.site.site_header = "FinCore Administration"
admin.site.site_title = "FinCore Admin"
admin.site.index_title = "Accounting & Inventory Management"