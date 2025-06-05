from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, PaymentMethod, Sale, SaleItem, Supplier, Purchase, Expense, FinancialReport, ProductionBatch, Recipe
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.db.models import Sum, Count, F
from .forms import ProductForm, ExpenseForm, RecipeForm, ProductionBatchForm, SupplierForm

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'core/product_list.html', {'products': products})

@login_required
def pos(request):
    products = Product.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    return render(request, 'core/pos.html', {
        'products': products,
        'payment_methods': payment_methods
    })

@csrf_exempt
def process_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_name = data.get('customer_name', 'Walk-in Customer')
            payment_method = data.get('payment_method')
            items = data.get('items', [])

            # Create sale
            sale = Sale.objects.create(
                customer_name=customer_name,
                total_amount=0,  # Will be updated
                payment_method=payment_method
            )

            total_amount = 0
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                
                # Check if enough stock
                if product.stock_quantity < quantity:
                    sale.delete()
                    return JsonResponse({
                        'success': False,
                        'error': f'Not enough stock for {product.name}'
                    })

                # Create sale item
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                total_amount += sale_item.total_price

            # Update sale total
            sale.total_amount = total_amount
            sale.save()

            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'total_amount': total_amount
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def purchase_list(request):
    purchases = Purchase.objects.all().order_by('-purchase_date')
    pending_orders = purchases.filter(status='pending')
    ordered_orders = purchases.filter(status='ordered')
    delivered_orders = purchases.filter(status='delivered')
    
    context = {
        'purchases': purchases,
        'pending_orders': pending_orders,
        'ordered_orders': ordered_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'core/purchase_list.html', context)

@login_required
def update_purchase_status(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Purchase.STATUS_CHOICES):
            purchase.status = new_status
            
            # Update dates based on status
            if new_status == 'ordered':
                purchase.order_date = timezone.now()
            elif new_status == 'delivered':
                purchase.delivery_date = timezone.now()
                # Update stock only when delivered
                purchase.product.stock_quantity += purchase.quantity
                purchase.product.save()
            
            purchase.save()
            messages.success(request, f'Order status updated to {new_status}')
            
    return redirect('order_dashboard')

@login_required
def order_dashboard(request):
    # Get counts for different order statuses
    pending_count = Purchase.objects.filter(status='pending').count()
    ordered_count = Purchase.objects.filter(status='ordered').count()
    delivered_count = Purchase.objects.filter(status='delivered').count()
    manual_pickups_count = Purchase.objects.filter(delivery_method='manual').count()
    
    # Get recent orders
    recent_orders = Purchase.objects.all().order_by('-purchase_date')[:10]
    
    # Get orders that need attention (pending or ordered for more than 3 days)
    attention_needed = Purchase.objects.filter(
        status__in=['pending', 'ordered'],
        purchase_date__lte=timezone.now() - timedelta(days=3)
    )
    
    # Get upcoming deliveries (ordered but not delivered, with expected delivery date)
    upcoming_deliveries = Purchase.objects.filter(
        status='ordered',
        expected_delivery_date__isnull=False
    ).order_by('expected_delivery_date')
    
    context = {
        'pending_count': pending_count,
        'ordered_count': ordered_count,
        'delivered_count': delivered_count,
        'manual_pickups_count': manual_pickups_count,
        'recent_orders': recent_orders,
        'attention_needed': attention_needed,
        'upcoming_deliveries': upcoming_deliveries,
    }
    return render(request, 'core/order_dashboard.html', context)

@login_required
def add_purchase(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier_id = data.get('supplier_id')
            product_id = data.get('product_id')
            quantity = int(data.get('quantity'))
            unit_price = float(data.get('unit_price'))
            notes = data.get('notes', '')

            supplier = get_object_or_404(Supplier, id=supplier_id)
            product = get_object_or_404(Product, id=product_id)

            purchase = Purchase.objects.create(
                supplier=supplier,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                notes=notes
            )

            return JsonResponse({
                'success': True,
                'purchase_id': purchase.id,
                'total_amount': purchase.total_amount
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    suppliers = Supplier.objects.all()
    products = Product.objects.filter(is_active=True)
    return render(request, 'core/add_purchase.html', {
        'suppliers': suppliers,
        'products': products
    })

@login_required
def stock_report(request):
    products = Product.objects.all()
    low_stock = [p for p in products if p.needs_restock()]
    return render(request, 'core/stock_report.html', {
        'products': products,
        'low_stock': low_stock
    })

@login_required
def inventory_dashboard(request):
    products = Product.objects.all()
    total_products = products.count()
    low_stock = [p for p in products if p.needs_restock()]
    low_stock_count = len(low_stock)
    total_suppliers = Supplier.objects.count()
    total_stock_value = sum(p.stock_quantity * p.price for p in products)
    recent_purchases = Purchase.objects.all().order_by('-purchase_date')[:5]

    context = {
        'total_products': total_products,
        'low_stock': low_stock,
        'low_stock_count': low_stock_count,
        'total_suppliers': total_suppliers,
        'total_stock_value': total_stock_value,
        'recent_purchases': recent_purchases,
    }
    return render(request, 'core/inventory_dashboard.html', context)

@login_required
def dashboard(request):
    # Get today's sales
    today = timezone.now().date()
    today_sales = Sale.objects.filter(
        sale_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Get low stock items
    low_stock = Product.objects.filter(
        stock_quantity__lte=F('minimum_stock_level')
    )[:5]  # Show only top 5 low stock items

    # Get recent sales and purchases
    recent_sales = Sale.objects.all().order_by('-sale_date')[:5]
    recent_purchases = Purchase.objects.all().order_by('-purchase_date')[:5]

    context = {
        'today_sales': today_sales,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def import_export(request):
    if request.method == 'POST':
        if 'import_file' in request.FILES:
            file = request.FILES['import_file']
            if file.name.endswith('.csv'):
                # Handle CSV import
                reader = csv.DictReader(file.read().decode('utf-8').splitlines())
                for row in reader:
                    if 'product' in request.POST.get('import_type'):
                        Product.objects.create(
                            name=row['name'],
                            description=row['description'],
                            price=row['price'],
                            category=row['category'],
                            stock_quantity=row['stock_quantity'],
                            minimum_stock_level=row['minimum_stock_level'],
                            reorder_quantity=row['reorder_quantity']
                        )
                    elif 'supplier' in request.POST.get('import_type'):
                        Supplier.objects.create(
                            name=row['name'],
                            contact_person=row['contact_person'],
                            phone=row['phone'],
                            email=row['email'],
                            address=row['address']
                        )
                messages.success(request, 'Import completed successfully!')
            else:
                messages.error(request, 'Please upload a CSV file.')
    
    return render(request, 'core/import_export.html', {
        'products': Product.objects.all(),
        'suppliers': Supplier.objects.all()
    })

@login_required
def export_data(request):
    data_type = request.GET.get('type', 'products')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if data_type == 'products':
        writer.writerow(['name', 'description', 'price', 'category', 'stock_quantity', 'minimum_stock_level', 'reorder_quantity'])
        for product in Product.objects.all():
            writer.writerow([
                product.name,
                product.description,
                product.price,
                product.category,
                product.stock_quantity,
                product.minimum_stock_level,
                product.reorder_quantity
            ])
    elif data_type == 'suppliers':
        writer.writerow(['name', 'contact_person', 'phone', 'email', 'address'])
        for supplier in Supplier.objects.all():
            writer.writerow([
                supplier.name,
                supplier.contact_person,
                supplier.phone,
                supplier.email,
                supplier.address
            ])
    elif data_type == 'purchases':
        writer.writerow(['date', 'supplier', 'product', 'quantity', 'unit_price', 'total_amount'])
        for purchase in Purchase.objects.all():
            writer.writerow([
                purchase.purchase_date,
                purchase.supplier.name,
                purchase.product.name,
                purchase.quantity,
                purchase.unit_price,
                purchase.total_amount
            ])
    
    return response

@login_required
def financial_dashboard(request):
    # Get financial data
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Get monthly sales
    monthly_sales = Sale.objects.filter(
        created_at__date__gte=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get monthly expenses
    monthly_expenses = Expense.objects.filter(
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent expenses
    recent_expenses = Expense.objects.all().order_by('-date')[:5]
    
    # Get recent financial reports
    recent_reports = FinancialReport.objects.all().order_by('-created_at')[:5]
    
    context = {
        'monthly_sales': monthly_sales,
        'monthly_expenses': monthly_expenses,
        'monthly_profit': monthly_sales - monthly_expenses,
        'recent_expenses': recent_expenses,
        'recent_reports': recent_reports,
    }
    return render(request, 'core/financial_dashboard.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('financial_dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'core/add_expense.html', {'form': form})

@login_required
def production_dashboard(request):
    # Get production data
    today = timezone.now().date()
    
    # Get active batches
    active_batches = ProductionBatch.objects.filter(
        status__in=['planned', 'in_progress']
    ).order_by('planned_date')
    
    # Get completed batches
    completed_batches = ProductionBatch.objects.filter(
        status='completed',
        actual_date=today
    )
    
    # Get recipes
    recipes = Recipe.objects.all()
    
    context = {
        'active_batches': active_batches,
        'completed_batches': completed_batches,
        'recipes': recipes,
    }
    return render(request, 'core/production_dashboard.html', context)

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipe added successfully!')
            return redirect('production_dashboard')
    else:
        form = RecipeForm()
    return render(request, 'core/add_recipe.html', {'form': form})

@login_required
def add_production_batch(request):
    if request.method == 'POST':
        form = ProductionBatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            messages.success(request, f'Production batch {batch.batch_number} has been created successfully!')
            return redirect('production_dashboard')
    else:
        # Generate a new batch number
        last_batch = ProductionBatch.objects.order_by('-batch_number').first()
        next_batch_number = f"B{datetime.now().strftime('%Y%m%d')}001"
        if last_batch:
            try:
                last_number = int(last_batch.batch_number[-3:])
                next_batch_number = f"B{datetime.now().strftime('%Y%m%d')}{(last_number + 1):03d}"
            except (ValueError, IndexError):
                pass
        
        form = ProductionBatchForm(initial={'batch_number': next_batch_number})
    
    return render(request, 'core/add_production_batch.html', {
        'form': form,
        'recipes': Recipe.objects.filter(is_active=True)
    })

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'core/delete_product.html', {'product': product})

@login_required
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    # Check if supplier has any associated products or purchases
    has_products = supplier.products.exists()
    has_purchases = supplier.purchases.exists()
    
    if request.method == 'POST':
        if not has_products and not has_purchases:
            supplier.delete()
            messages.success(request, 'Supplier deleted successfully!')
            return redirect('supplier_list')
        else:
            messages.error(request, 'Cannot delete supplier with associated products or purchases.')
            return redirect('supplier_list')
            
    return render(request, 'core/delete_supplier.html', {
        'supplier': supplier,
        'has_products': has_products,
        'has_purchases': has_purchases
    })

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'core/supplier_list.html', {
        'suppliers': suppliers
    })

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'core/add_supplier.html', {'form': form})

@login_required
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'core/edit_supplier.html', {'form': form, 'supplier': supplier})

@login_required
def dashboard_data(request):
    """API endpoint to provide dashboard data in JSON format."""
    total_products = Product.objects.count()
    low_stock = Product.objects.filter(stock_quantity__lte=F('minimum_stock_level'))
    low_stock_count = low_stock.count()
    total_suppliers = Supplier.objects.count()
    total_stock_value = Product.objects.aggregate(
        total=Sum(F('stock_quantity') * F('purchase_price'))
    )['total'] or 0

    recent_purchases = Purchase.objects.select_related('product').order_by('-purchase_date')[:5]

    data = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_suppliers': total_suppliers,
        'total_stock_value': float(total_stock_value),
        'low_stock': [
            {
                'id': product.id,
                'name': product.name,
                'stock_quantity': product.stock_quantity,
                'minimum_stock_level': product.minimum_stock_level
            }
            for product in low_stock
        ],
        'recent_purchases': [
            {
                'purchase_date': purchase.purchase_date.strftime('%Y-%m-%d'),
                'product_name': purchase.product.name,
                'quantity': purchase.quantity,
                'total_amount': float(purchase.total_amount)
            }
            for purchase in recent_purchases
        ]
    }

    return JsonResponse(data)

@login_required
def supply_receipt(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, 'core/supply_receipt.html', {
        'purchase': purchase
    })
