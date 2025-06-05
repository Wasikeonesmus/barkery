from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('bread', 'Bread'),
        ('cake', 'Cake'),
        ('pastry', 'Pastry'),
        ('cookie', 'Cookie'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products')
    stock_quantity = models.IntegerField(default=0)
    minimum_stock_level = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=20)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def needs_restock(self):
        return self.stock_quantity <= self.minimum_stock_level

    class Meta:
        ordering = ['name']

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('manual', 'Manual Pickup'),
        ('supplier_delivery', 'Supplier Delivery'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)
    order_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='supplier_delivery')
    delivery_person = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    checked_by = models.CharField(max_length=100, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    supplier_notes = models.TextField(blank=True, null=True, help_text="Notes from supplier or delivery instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase #{self.id} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        self.debt = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)
        # Update product stock
        if self.status == 'delivered':
            self.product.stock_quantity += self.quantity
            self.product.save()

    class Meta:
        ordering = ['-purchase_date']

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Payment'),
    ]
    
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-PESA'),
        ('card', 'Card'),
    ]

    customer_name = models.CharField(max_length=100, default="Walk-in Customer")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    sale_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name}"

    class Meta:
        ordering = ['-sale_date']

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update product stock
        self.product.stock_quantity -= self.quantity
        self.product.save()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

class Expense(models.Model):
    EXPENSE_TYPES = [
        ('ingredients', 'Ingredients'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('equipment', 'Equipment'),
        ('salaries', 'Salaries'),
        ('other', 'Other'),
    ]
    
    date = models.DateField()
    type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.date} - {self.type} - ${self.amount}"

class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    start_date = models.DateField()
    end_date = models.DateField()
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.report_type.capitalize()} Report ({self.start_date} to {self.end_date})"

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField(help_text="List of ingredients and their quantities")
    instructions = models.TextField(help_text="Step-by-step instructions")
    preparation_time = models.IntegerField(help_text="Preparation time in minutes")
    yield_quantity = models.IntegerField(help_text="Expected yield quantity")
    yield_unit = models.CharField(max_length=50, help_text="Unit of measurement (e.g., pieces, kg)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ProductionBatch(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=20, unique=True)
    planned_date = models.DateField()
    planned_start_time = models.TimeField(default='08:00')
    planned_end_time = models.TimeField(default='17:00')
    actual_date = models.DateField(null=True, blank=True)
    quantity_produced = models.IntegerField(default=0)
    quality_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Batch {self.batch_number} - {self.recipe.name}"
