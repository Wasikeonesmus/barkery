from django.contrib import admin
from .models import Product, PaymentMethod, Sale, SaleItem, Supplier, Purchase, Expense, FinancialReport, Recipe, ProductionBatch

# Customize the admin site
admin.site.site_header = 'Bakery Management System'
admin.site.site_title = 'Bakery Admin'
admin.site.index_title = 'Welcome to Bakery Management'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'created_at')
    search_fields = ('name', 'contact_person', 'phone', 'email')
    list_filter = ('created_at',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'supplier', 'needs_restock', 'is_active')
    list_filter = ('category', 'supplier', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'minimum_stock_level', 'reorder_quantity')
        }),
        ('Supplier Information', {
            'fields': ('supplier',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def needs_restock(self, obj):
        return obj.needs_restock()
    needs_restock.boolean = True
    needs_restock.short_description = 'Needs Restock'

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'quantity', 'unit_price', 'total_amount', 'purchase_date')
    list_filter = ('supplier', 'purchase_date')
    search_fields = ('product__name', 'supplier__name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'purchase_date'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update product stock
        obj.product.stock_quantity += obj.quantity
        obj.product.save()

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'payment_method', 'sale_date')
    list_filter = ('payment_method', 'sale_date')
    search_fields = ('customer_name',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SaleItemInline]
    date_hierarchy = 'sale_date'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'amount', 'description')
    list_filter = ('type', 'date')
    search_fields = ('description',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'start_date', 'end_date', 'total_sales', 'total_expenses', 'net_profit')
    list_filter = ('report_type', 'start_date')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'preparation_time', 'yield_quantity', 'yield_unit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'ingredients')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Production Information', {
            'fields': ('preparation_time', 'yield_quantity', 'yield_unit')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'recipe', 'planned_date', 'status', 'quantity_produced')
    list_filter = ('status', 'planned_date')
    search_fields = ('batch_number', 'recipe__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'planned_date'
    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_number', 'recipe', 'status')
        }),
        ('Schedule', {
            'fields': ('planned_date', 'planned_start_time', 'planned_end_time')
        }),
        ('Production Details', {
            'fields': ('quantity_produced', 'quality_notes', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
